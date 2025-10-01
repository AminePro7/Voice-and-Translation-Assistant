"""
RAG-based Assistant Service using shared voice assistant modules
"""

import sys
from pathlib import Path
import random

# Add shared modules to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.base.voice_assistant import BaseVoiceAssistant

# RAG and LLM imports
try:
    from langchain_ollama import OllamaLLM, OllamaEmbeddings
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import FAISS
    from langchain.prompts import (
        ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate,
        MessagesPlaceholder, PromptTemplate
    )
    from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
    from langchain.schema.output_parser import StrOutputParser
    from langchain_core.documents import Document
    from langchain.memory import ConversationBufferMemory
    from operator import itemgetter
    from langchain.schema import AIMessage, HumanMessage
    import numpy as np
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"ERROR: Langchain libraries are missing ({e}).")
    print("Install them with: pip install langchain langchain-community langchain-ollama faiss-cpu")
    LANGCHAIN_AVAILABLE = False
    sys.exit(1)


class RAGAssistant(BaseVoiceAssistant):
    """
    RAG-based voice assistant that extends BaseVoiceAssistant
    Provides conversational AI with document-based knowledge retrieval
    """
    
    # RAG Configuration
    EMBEDDING_MODEL_NAME = 'embeddinggemma:latest'  # Ollama embedding model
    CHUNK_SIZE = 300  # Smaller chunks to reduce embedding load
    CHUNK_OVERLAP = 30
    SEARCH_K = 3
    
    # Pre-defined responses for natural conversation
    responses = {
        'reassuring': [
            "T'inquiète, tu n'es pas le seul, ça arrive souvent.",
            "Je suis là pour t'aider, on va faire ça ensemble.",
            "Pas de panique, on va y aller doucement.",
            "On va gérer ça, étape par étape, tu vas voir.",
            "Ce genre de souci se règle vite, suis-moi."
        ],
        'thinking': [
            "Je traite ta demande...",
            "J'analyse la situation...", 
            "Je cherche la meilleure approche...",
            "Je vérifie les détails...",
            "Je prépare une réponse adaptée..."
        ]
    }
    
    common_responses = {
        "bonjour": "Bonjour! Comment puis-je vous aider aujourd'hui ?",
        "salut": "Bonjour! Comment puis-je vous aider aujourd'hui ?",
        "ça va": "Je vais bien, merci. Comment puis-je vous aider ?",
        "comment vas-tu": "Je vais bien, merci. Comment puis-je vous aider ?",
        "merci": "De rien ! Si vous avez d'autres questions, n'hésitez pas.",
        "au revoir": "Au revoir et bonne journée !"
    }
    
    def __init__(self, doc_path=None, ollama_model="gemma3:1b", embedding_model="embeddinggemma:latest", whisper_model='small'):
        """
        Initialize RAG assistant
        
        Args:
            doc_path: Path to knowledge base document
            ollama_model: Name of Ollama model to use (default: gemma3:1b)
            embedding_model: Name of Ollama embedding model (default: embeddinggemma:latest)
            whisper_model: Whisper model size
        """
        # Initialize base voice assistant
        super().__init__("RAGAssistant", whisper_model)
        
        if not LANGCHAIN_AVAILABLE:
            raise RuntimeError("Langchain dependencies are not available. The service cannot start.")
        
        # Set up paths (now using backed up files)
        if doc_path is None:
            doc_path = self.paths.root_dir / "backup_important_files" / "doc_resolutions.md"
        
        self.doc_path = Path(doc_path)
        self.ollama_model = ollama_model
        self.embedding_model = embedding_model
        self.vectorstore_dir = self.paths.root_dir / "backup_important_files" / "vectorstore_faiss_md"
        
        # Verify essential files
        self._verify_files()
        
        # Initialize RAG components
        self._init_rag_system()
        
        self.logger.info("RAG Assistant initialization completed")
    
    def _verify_files(self):
        """Verify that all required files exist"""
        essential_files = {
            self.doc_path: "Knowledge base document"
        }
        
        for file_path, description in essential_files.items():
            if not file_path.exists():
                raise FileNotFoundError(f"{description} not found at {file_path}")
            self.logger.info(f"Found {description} at {file_path}")
        
        # Log Ollama models being used
        self.logger.info(f"Using Ollama LLM model: {self.ollama_model}")
        self.logger.info(f"Using Ollama embedding model: {self.embedding_model}")
    
    def _init_rag_system(self):
        """Initialize RAG system components"""
        self.logger.info("Initializing RAG system...")
        
        # Initialize Ollama embeddings
        self.logger.info(f"Initializing Ollama embedding model: {self.embedding_model}")
        self.embeddings = OllamaEmbeddings(
            model=self.embedding_model
        )
        self.logger.info("Ollama embedding model initialized successfully")
        
        # Load or create vector store
        self._load_or_create_vectorstore()
        
        # Initialize LLM
        self._init_llm()
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Create RAG chain
        self._create_rag_chain()
        
        # Set ultra-high sensitivity for better voice detection
        self.set_sensitivity_preset('ultra_sensitive')  # Ultra-maximum sensitivity for very quiet speech
        
        self.logger.info("RAG system initialized successfully")
    
    def _load_or_create_vectorstore(self):
        """Load existing vectorstore or create new one"""
        if self.vectorstore_dir.exists():
            self.logger.info("Loading existing vector store...")
            self.vectorstore = FAISS.load_local(
                str(self.vectorstore_dir),
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            self.logger.info("Creating new vector store...")
            self._create_vectorstore()
    
    def _create_vectorstore(self):
        """Create vector store from knowledge base document"""
        # Load document
        with open(self.doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.CHUNK_SIZE,
            chunk_overlap=self.CHUNK_OVERLAP
        )
        
        chunks = text_splitter.split_text(content)
        documents = [Document(page_content=chunk) for chunk in chunks]
        
        self.logger.info(f"Created {len(documents)} document chunks")
        
        # Process documents in smaller batches to avoid overwhelming Ollama
        batch_size = 50  # Process 50 documents at a time
        self.logger.info(f"Processing documents in batches of {batch_size}")
        
        vectorstore = None
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            self.logger.info(f"Processing batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size} ({len(batch)} documents)")
            
            try:
                if vectorstore is None:
                    # Create initial vector store with first batch
                    vectorstore = FAISS.from_documents(batch, self.embeddings)
                else:
                    # Add subsequent batches to existing vector store
                    batch_vectorstore = FAISS.from_documents(batch, self.embeddings)
                    vectorstore.merge_from(batch_vectorstore)
                
                self.logger.info(f"Batch {i//batch_size + 1} processed successfully")
            except Exception as e:
                self.logger.error(f"Failed to process batch {i//batch_size + 1}: {e}")
                raise
        
        self.vectorstore = vectorstore
        
        # Save vector store
        self.vectorstore_dir.parent.mkdir(exist_ok=True)
        self.vectorstore.save_local(str(self.vectorstore_dir))
        
        self.logger.info(f"Vector store saved to {self.vectorstore_dir}")
    
    def _init_llm(self):
        """Initialize Ollama LLM model"""
        self.logger.info(f"Initializing Ollama LLM: {self.ollama_model}")
        
        try:
            self.llm = OllamaLLM(
                model=self.ollama_model,
                temperature=0.7,
                num_predict=256,  # max_tokens equivalent for Ollama
                top_p=1.0,
                verbose=False
            )
            self.logger.info("Ollama LLM initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama LLM: {e}")
            raise RuntimeError(f"Ollama LLM initialization failed: {e}") from e
    
    def _create_rag_chain(self):
        """Create RAG processing chain"""
        # Create retriever
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": self.SEARCH_K}
        )
        
        # Create prompt template
        system_prompt = """Tu es un assistant technique français compétent et serviable. 
        Utilise le contexte suivant pour répondre aux questions de manière claire et précise.
        Si tu ne trouves pas l'information dans le contexte, dis-le clairement.
        Sois concis mais informatif.
        
        Contexte: {context}
        
        Historique: {chat_history}"""
        
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template("Question: {question}")
        ])
        
        # Create processing chain
        def format_docs(docs):
            return "\n\n".join([doc.page_content for doc in docs])
        
        def log_and_format_docs(docs):
            """Log retrieved documents and format them"""
            if docs:
                self.logger.info(f"RAG Retrieved {len(docs)} documents:")
                for i, doc in enumerate(docs, 1):
                    # Log first 100 characters of each document for reference
                    content_preview = doc.page_content[:100].replace('\n', ' ').strip()
                    if len(doc.page_content) > 100:
                        content_preview += "..."
                    self.logger.info(f"  Doc {i}: {content_preview}")
            else:
                self.logger.info("RAG: No documents retrieved")
            return format_docs(docs)
        
        def get_chat_history(memory):
            return memory.chat_memory.messages if hasattr(memory, 'chat_memory') else []
        
        self.rag_chain = (
            {
                "context": self.retriever | log_and_format_docs,
                "question": RunnablePassthrough(),
                "chat_history": lambda x: get_chat_history(self.memory)
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
    
    def process_user_input(self, text):
        """
        Process user input through RAG system
        
        Args:
            text: User input text
        
        Returns:
            Assistant response text
        """
        try:
            # Check for common responses
            text_lower = text.lower()
            for key, response in self.common_responses.items():
                if key in text_lower:
                    return response
            
            # Use RAG system for complex queries
            self.logger.info(f"Processing query: '{text}'")
            
            # Get response from RAG chain
            response = self.rag_chain.invoke(text)
            
            # Add to conversation memory
            self.memory.chat_memory.add_user_message(text)
            self.memory.chat_memory.add_ai_message(response)
            
            self.logger.info(f"Generated response: '{response}'")
            return response.strip()
            
        except Exception as e:
            self.logger.exception(f"Error processing user input: {e}")
            return "Désolé, une erreur interne est survenue. Pouvez-vous reformuler votre question ?"
    
    def run_interactive_session(self):
        """Run the main RAG assistant loop"""
        try:
            self.logger.info("Starting interactive RAG session")
            
            # Welcome message
            welcome_msg = "Bonjour, Expertise Bureautique chez Cloud Telecom. Bonjour, Comment puis-je vous aider ?"
            print(f"\n=== RAG Voice Assistant ===")
            print(welcome_msg)
            
            # Speak welcome message
            self.speak(welcome_msg, "fr_FR")
            
            while True:
                try:
                    print("\nÉcoute... (Parlez maintenant)")
                    print("🎤 Transcription temps réel avec détection intelligente du silence")
                    
                    # Use real-time transcription with silence detection (same as translation service)
                    transcribed_text = self.transcribe_realtime(
                        language="fr",
                        visual_feedback=True
                    )
                    
                    if not self.is_text_valid(transcribed_text):
                        no_speech_msg = "Je n'ai pas bien entendu. Pourriez-vous répéter plus clairement s'il vous plaît ?"
                        print("No valid speech detected.")
                        self.speak(no_speech_msg, "fr_FR")
                        continue
                    
                    print(f"You said: {transcribed_text}")
                    
                    # Check for exit commands
                    if self._is_exit_command(transcribed_text):
                        break
                    
                    # Play thinking sound and show thinking message
                    thinking_msg = random.choice(self.responses['thinking'])
                    print(f"Assistant: {thinking_msg}")
                    self.play_sound_file('model_is_thinking.mp3')
                    
                    # Process input through RAG
                    response = self.process_user_input(transcribed_text)
                    
                    print(f"Assistant: {response}")
                    
                    # Play result sound
                    self.play_sound_file('result.mp3')
                    
                    # Speak response using chunks for long responses
                    if len(response) > 150:
                        self.speak_chunks(response, "fr_FR", max_chunk_length=120)
                    else:
                        self.speak(response, "fr_FR")
                    
                except KeyboardInterrupt:
                    print("\nSession interrompue par l'utilisateur")
                    break
                except Exception as e:
                    self.logger.exception(f"Erreur dans la boucle de session: {e}")
                    print(f"Une erreur s'est produite: {e}")
                    continue
            
        except Exception as e:
            self.logger.exception(f"Erreur fatale dans la session interactive: {e}")
            print(f"Le service a échoué: {e}")
        
        finally:
            print("\nAu revoir!")
            self.speak("Au revoir et bonne journée !", "fr_FR")
    
    def _is_exit_command(self, text):
        """Check if text contains exit command"""
        exit_commands = ['quitter', 'sortir', 'arrêter', 'au revoir', 'bye', 'exit', 'quit']
        text_lower = text.lower()
        return any(cmd in text_lower for cmd in exit_commands)

def main():
    """Main entry point for RAG assistant service"""
    import argparse
    
    parser = argparse.ArgumentParser(description='RAG Voice Assistant Service with Ollama')
    parser.add_argument(
        '--doc-path',
        type=str,
        help='Path to knowledge base document'
    )
    parser.add_argument(
        '--ollama-model',
        type=str,
        default='gemma3:1b',
        help='Ollama LLM model name (default: gemma3:1b)'
    )
    parser.add_argument(
        '--embedding-model',
        type=str,
        default='embeddinggemma:latest',
        help='Ollama embedding model name (default: embeddinggemma:latest)'
    )
    parser.add_argument(
        '--whisper-model',
        choices=['tiny', 'small', 'medium', 'large'],
        default='small',
        help='Whisper model size (default: small)'
    )
    
    args = parser.parse_args()
    
    print("🤖 Initializing RAG Assistant Service with Ollama...")
    print(f"   - LLM Model: {args.ollama_model}")
    print(f"   - Embedding Model: {args.embedding_model}")
    print(f"   - Whisper Model: {args.whisper_model}")
    
    try:
        with RAGAssistant(
            doc_path=args.doc_path,
            ollama_model=args.ollama_model,
            embedding_model=args.embedding_model,
            whisper_model=args.whisper_model
        ) as service:
            service.run_interactive_session()
    except KeyboardInterrupt:
        print("\nService stopped by user")
    except Exception as e:
        print(f"Service failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()