"""Knowledge manager implementation."""

from typing import Dict, List, Optional
from app.services.knowledge.manager_interface import IKnowledgeManager

class KnowledgeManager(IKnowledgeManager):
    """Manages storage and retrieval of knowledge entries.
    
    This implementation uses in-memory storage, but is designed to be
    replaced with a proper database implementation in production.
    """
    
    def __init__(self):
        """Initialize the knowledge manager with empty storage."""
        # For now, we store knowledge in an in-memory dictionary.
        # In production, this would be replaced with a database.
        self.knowledge_data: Dict[str, Dict] = {}
    
    def upload_knowledge(self, topic: str, content: str, tags: Optional[List[str]] = None) -> Dict:
        """Store new knowledge entry.
        
        Args:
            topic (str): Topic/title for the knowledge
            content (str): Knowledge content
            tags (List[str], optional): Tags for categorization
            
        Returns:
            Dict: Upload result status
        """
        self.knowledge_data[topic] = {
            "content": content,
            "tags": tags or []
        }
        return {
            "status": "success",
            "message": f"Knowledge '{topic}' uploaded successfully"
        }
    
    def retrieve_knowledge(self, query: str) -> Dict:
        """Retrieve knowledge based on query.
        
        Args:
            query (str): Search query or topic name
            
        Returns:
            Dict: Retrieved knowledge or search results
        """
        # Simple implementation: direct topic lookup or basic search
        if query in self.knowledge_data:
            return {
                "status": "success",
                "topic": query,
                "content": self.knowledge_data[query]["content"],
                "tags": self.knowledge_data[query]["tags"]
            }
        
        # Basic search implementation
        results = []
        for topic, data in self.knowledge_data.items():
            if (query.lower() in topic.lower() or 
                query.lower() in data["content"].lower() or
                any(query.lower() in tag.lower() for tag in data["tags"])):
                results.append({
                    "topic": topic,
                    "preview": data["content"][:100] + "..." if len(data["content"]) > 100 else data["content"],
                    "tags": data["tags"]
                })
        
        return {
            "status": "success" if results else "not_found",
            "results": results,
            "count": len(results)
        }
    
    def list_topics(self) -> List[Dict]:
        """List all available knowledge topics.
        
        Returns:
            List[Dict]: List of topics with metadata
        """
        return [
            {"topic": topic, "tags": data["tags"]}
            for topic, data in self.knowledge_data.items()
        ]
    
    def update_knowledge(self, topic: str, new_content: str, tags: Optional[List[str]] = None) -> Dict:
        """Update existing knowledge entry.
        
        Args:
            topic (str): Topic to update
            new_content (str): New content
            tags (List[str], optional): Updated tags
            
        Returns:
            Dict: Update result status
        """
        if topic not in self.knowledge_data:
            return {
                "status": "error",
                "message": f"Topic '{topic}' not found"
            }
        
        # Update content
        self.knowledge_data[topic]["content"] = new_content
        
        # Update tags if provided
        if tags is not None:
            self.knowledge_data[topic]["tags"] = tags
        
        return {
            "status": "success",
            "message": f"Knowledge '{topic}' updated successfully"
        }
    
    def delete_knowledge(self, topic: str) -> Dict:
        """Delete knowledge entry.
        
        Args:
            topic (str): Topic to delete
            
        Returns:
            Dict: Deletion result status
        """
        if topic not in self.knowledge_data:
            return {
                "status": "error",
                "message": f"Topic '{topic}' not found"
            }
        
        del self.knowledge_data[topic]
        return {
            "status": "success",
            "message": f"Knowledge '{topic}' deleted successfully"
        } 