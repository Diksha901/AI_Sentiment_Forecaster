"""
RAG API Routes
FastAPI endpoints for RAG operations
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from oauth2 import verify_access_token
from fastapi.security import OAuth2PasswordBearer

from rag.rag_service import get_rag_engine
from rag.document_processor import DocumentProcessor
from pymongo import MongoClient

# Initialize router
router = APIRouter(
    prefix="/api/rag",
    tags=["RAG - Retrieval Augmented Generation"]
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# MongoDB connection (reuse from main server)
try:
    client = MongoClient(
        "mongodb+srv://DevanshVerma:qazxsw123@cluster0.fxr8rpr.mongodb.net/ai_project_db?retryWrites=true&w=majority&appName=Cluster0",
        serverSelectionTimeoutMS=5000
    )
    db = client["ai_project_db"]
    product_collection = db["product_results"]
    news_collection = db["news_results"]
except Exception as e:
    print(f"⚠ MongoDB connection failed in RAG router: {e}")


# Request/Response Models
class QueryRequest(BaseModel):
    question: str = Field(..., description="User question")
    category: Optional[str] = Field(None, description="Filter by category")
    sentiment: Optional[str] = Field(None, description="Filter by sentiment")
    return_sources: bool = Field(True, description="Return source documents")


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: Optional[List[Dict[str, Any]]] = None
    source_count: Optional[int] = None
    success: bool


class IndexRequest(BaseModel):
    source: str = Field(..., description="Data source: 'mongodb' or 'all'")
    doc_type: Optional[str] = Field("all", description="Document type: 'review', 'news', or 'all'")
    limit: Optional[int] = Field(None, description="Limit number of documents to index")


class IndexResponse(BaseModel):
    success: bool
    message: str
    indexed_count: int
    errors: Optional[List[str]] = None


# -----------------------
# RAG Query Endpoints
# -----------------------

@router.get("/")
def rag_info():
    """Get RAG system information"""
    return {
        "message": "RAG (Retrieval-Augmented Generation) API",
        "version": "1.0.0",
        "endpoints": {
            "POST /query": "Ask questions with contextual retrieval",
            "POST /insights": "Get contextual insights",
            "POST /index/mongodb": "Index documents from MongoDB",
            "GET /sentiment-summary": "Get sentiment summary",
            "GET /trending-topics": "Get trending topics",
            "GET /stats": "Get RAG system statistics"
        }
    }


@router.post("/query", response_model=QueryResponse)
def query_rag(
    request: QueryRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    Query the RAG system with natural language
    
    Example:
    ```
    {
        "question": "What are customers saying about electronics?",
        "category": "electronics",
        "sentiment": "Positive"
    }
    ```
    """
    # Verify token
    verify_access_token(token)
    
    # Get RAG engine
    rag_engine = get_rag_engine()
    if not rag_engine:
        raise HTTPException(
            status_code=503,
            detail="RAG system not initialized. Please configure API keys and install dependencies."
        )
    
    # Query with filters if provided
    if request.category or request.sentiment:
        result = rag_engine.query_with_filters(
            question=request.question,
            category=request.category,
            sentiment=request.sentiment
        )
    else:
        result = rag_engine.query(
            question=request.question,
            return_sources=request.return_sources
        )
    
    return result


@router.post("/insights")
def get_insights(
    query: str,
    context_type: str = "all",
    token: str = Depends(oauth2_scheme)
):
    """
    Get contextual insights based on query
    
    Args:
        query: User query
        context_type: Type of context ('reviews', 'news', 'all')
    """
    verify_access_token(token)
    
    rag_engine = get_rag_engine()
    if not rag_engine:
        raise HTTPException(
            status_code=503,
            detail="RAG system not available"
        )
    
    return rag_engine.get_contextual_insights(query, context_type)


@router.get("/sentiment-summary")
def sentiment_summary(
    category: Optional[str] = None,
    token: str = Depends(oauth2_scheme)
):
    """
    Get sentiment summary for a category
    
    Args:
        category: Product category (optional)
    """
    verify_access_token(token)
    
    rag_engine = get_rag_engine()
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    return rag_engine.get_sentiment_summary(category)


@router.get("/trending-topics")
def trending_topics(
    limit: int = 5,
    token: str = Depends(oauth2_scheme)
):
    """
    Get trending topics from consumer discussions
    
    Args:
        limit: Number of topics to return
    """
    verify_access_token(token)
    
    rag_engine = get_rag_engine()
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    return rag_engine.get_trending_topics(limit)


@router.post("/compare-categories")
def compare_categories(
    categories: List[str],
    token: str = Depends(oauth2_scheme)
):
    """
    Compare sentiment across multiple categories
    
    Args:
        categories: List of categories to compare
    """
    verify_access_token(token)
    
    rag_engine = get_rag_engine()
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    return rag_engine.compare_products(categories)


# -----------------------
# Document Indexing Endpoints
# -----------------------

@router.post("/index/mongodb", response_model=IndexResponse)
def index_from_mongodb(
    request: IndexRequest,
    token: str = Depends(oauth2_scheme)
):
    """
    Index documents from MongoDB into vector store
    
    Example:
    ```
    {
        "source": "mongodb",
        "doc_type": "all",
        "limit": 100
    }
    ```
    """
    verify_access_token(token)
    
    rag_engine = get_rag_engine()
    if not rag_engine:
        raise HTTPException(
            status_code=503,
            detail="RAG system not initialized"
        )
    
    processor = DocumentProcessor()
    all_chunks = []
    errors = []
    
    try:
        # Index product reviews
        if request.doc_type in ["review", "all"]:
            try:
                reviews = list(product_collection.find().limit(request.limit or 0))
                if reviews:
                    review_chunks = processor.process_batch_from_mongodb(reviews, "review")
                    all_chunks.extend(review_chunks)
                    print(f"✓ Processed {len(review_chunks)} review chunks")
            except Exception as e:
                errors.append(f"Error processing reviews: {str(e)}")
        
        # Index news articles
        if request.doc_type in ["news", "all"]:
            try:
                news = list(news_collection.find().limit(request.limit or 0))
                if news:
                    news_chunks = processor.process_batch_from_mongodb(news, "news")
                    all_chunks.extend(news_chunks)
                    print(f"✓ Processed {len(news_chunks)} news chunks")
            except Exception as e:
                errors.append(f"Error processing news: {str(e)}")
        
        # Index documents
        if all_chunks:
            result = rag_engine.index_documents(all_chunks)
            
            return IndexResponse(
                success=result.get("success", False),
                message=f"Indexed {len(all_chunks)} document chunks from MongoDB",
                indexed_count=len(all_chunks),
                errors=errors if errors else None
            )
        else:
            return IndexResponse(
                success=False,
                message="No documents found to index",
                indexed_count=0,
                errors=errors if errors else None
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Indexing failed: {str(e)}"
        )


@router.get("/stats")
def get_stats(token: str = Depends(oauth2_scheme)):
    """Get RAG system statistics"""
    verify_access_token(token)
    
    rag_engine = get_rag_engine()
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    return rag_engine.get_stats()


@router.delete("/reset")
def reset_vector_store(token: str = Depends(oauth2_scheme)):
    """Reset/clear the vector store (admin only)"""
    verify_access_token(token)
    
    rag_engine = get_rag_engine()
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG system not available")
    
    try:
        rag_engine.vector_store_manager.delete_collection()
        return {"message": "Vector store cleared successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reset vector store: {str(e)}"
        )
