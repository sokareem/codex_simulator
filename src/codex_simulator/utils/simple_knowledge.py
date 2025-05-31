"""
A simple knowledge implementation that doesn't rely on OpenAI embeddings.
This provides a basic alternative to the CrewAI Knowledge class.
"""
from typing import Dict, Any, List
from pydantic import BaseModel, Field, computed_field

class SimpleKnowledge(BaseModel):
    """
    A simple knowledge class that stores content directly without embeddings.
    
    This class implements the minimum interface needed to be compatible with 
    CrewAI's Knowledge concept without requiring OpenAI API keys,
    though it's not directly assignable to Crew.knowledge.
    """
    
    content: Dict[str, str] = Field(description="Dictionary mapping document names to their text content")
    collection_name: str = Field(default="simple_knowledge", description="Name for this knowledge collection")

    @computed_field
    @property
    def sources(self) -> List[str]:
        """List of source document names, derived from content keys."""
        return list(self.content.keys())

    @computed_field
    @property
    def documents(self) -> List[str]: # For compatibility with crewAI.Knowledge if used elsewhere
        """List of document names, derived from content keys."""
        return list(self.content.keys())
        
    def query(self, query_text: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Simple query that just returns all documents (no actual semantic search).
        
        Args:
            query_text: The search query
            n_results: Number of results to return (ignored, returns all)
            
        Returns:
            List of document content with metadata
        """
        # Return all documents as if they all matched the query
        return [
            {
                "text": doc_content,
                "metadata": {"source": source_name},
                "score": 1.0  # Placeholder score
            }
            for source_name, doc_content in self.content.items()
        ]
