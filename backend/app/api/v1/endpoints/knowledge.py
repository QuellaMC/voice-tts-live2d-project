"""Knowledge management endpoints."""

from typing import List, Optional

from app.core.security import get_api_key, get_current_user
from app.database.session import get_db
from app.schemas.knowledge import (
    ConceptCreate,
    ConceptInDB,
    ConceptUpdate,
    KnowledgeCreate,
    KnowledgeList,
    KnowledgeResponse,
    KnowledgeUpdate,
    TagCreate,
    TagInDB,
    TagUpdate,
)
from app.services import (
    ConceptService,
    KnowledgeBatchService,
    KnowledgeService,
    TagService,
)
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

router = APIRouter()


# Knowledge endpoints
@router.post("/", response_model=KnowledgeResponse)
async def create_knowledge(
    *,
    knowledge_in: KnowledgeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> KnowledgeResponse:
    """Create new knowledge entry."""
    knowledge = await KnowledgeService().create_with_relations(
        db, obj_in=knowledge_in, user_id=current_user["id"]
    )
    return knowledge


@router.post("/batch", response_model=List[KnowledgeResponse])
async def create_knowledge_batch(
    *,
    items: List[KnowledgeCreate],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key)
) -> List[KnowledgeResponse]:
    """Create multiple knowledge entries in batch."""
    return await KnowledgeBatchService().create_many(
        db, items=items, user_id=current_user["id"]
    )


@router.get("/", response_model=KnowledgeList)
async def list_knowledge(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
    skip: int = 0,
    limit: int = 100,
    topic: Optional[str] = None,
    tag: Optional[str] = None,
    concept: Optional[str] = None,
) -> KnowledgeList:
    """List knowledge entries with filtering."""
    filters = {}
    if topic:
        filters["topic"] = topic
    if tag:
        filters["tags"] = {"name": tag}
    if concept:
        filters["concepts"] = {"name": concept}

    items = await KnowledgeService().get_multi(
        db, skip=skip, limit=limit, filters=filters
    )
    total = await KnowledgeService().count(db, filters=filters)

    return KnowledgeList(items=items, total=total, skip=skip, limit=limit)


@router.get("/{knowledge_id}", response_model=KnowledgeResponse)
async def get_knowledge(
    knowledge_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> KnowledgeResponse:
    """Get knowledge entry by ID."""
    knowledge = await KnowledgeService().get(db, id=knowledge_id)
    if not knowledge:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    return knowledge


@router.put("/{knowledge_id}", response_model=KnowledgeResponse)
async def update_knowledge(
    knowledge_id: int,
    knowledge_in: KnowledgeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> KnowledgeResponse:
    """Update knowledge entry."""
    knowledge = await KnowledgeService().get(db, id=knowledge_id)
    if not knowledge:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")

    knowledge = await KnowledgeService().update_with_audit(
        db, db_obj=knowledge, obj_in=knowledge_in, user_id=current_user["id"]
    )
    return knowledge


@router.delete("/{knowledge_id}", response_model=KnowledgeResponse)
async def delete_knowledge(
    knowledge_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> KnowledgeResponse:
    """Delete knowledge entry."""
    knowledge = await KnowledgeService().delete(db, id=knowledge_id)
    if not knowledge:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    return knowledge


@router.post("/search", response_model=List[KnowledgeResponse])
async def search_knowledge(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
    limit: int = 5,
    min_similarity: float = 0.7,
    tags: Optional[List[str]] = None,
    concepts: Optional[List[str]] = None,
) -> List[KnowledgeResponse]:
    """Search knowledge base using semantic similarity."""
    service = KnowledgeService()

    # Generate embedding for query
    query_embedding = await service._generate_embedding(query)
    if not query_embedding:
        raise HTTPException(
            status_code=500, detail="Failed to generate query embedding"
        )

    results = await service.search_similar(
        db,
        query_embedding=query_embedding,
        limit=limit,
        min_similarity=min_similarity,
        filter_tags=tags,
        filter_concepts=concepts,
    )
    return results


@router.post("/maintenance/cleanup", response_model=dict)
async def cleanup_knowledge_base(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
    days: int = Query(30, ge=1),
    background_tasks: BackgroundTasks = None,
) -> dict:
    """Clean up old entries and orphaned items."""
    if not background_tasks:
        raise HTTPException(status_code=500, detail="Background tasks not available")

    # Add cleanup tasks to background
    background_tasks.add_task(KnowledgeService().cleanup_old_entries, db=db, days=days)
    background_tasks.add_task(KnowledgeBatchService().cleanup_orphaned, db=db)

    return {"message": "Cleanup tasks scheduled"}


@router.post("/maintenance/reindex", response_model=dict)
async def reindex_embeddings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
    batch_size: int = Query(20, ge=1, le=100),
    background_tasks: BackgroundTasks = None,
) -> dict:
    """Reindex embeddings for all knowledge entries."""
    if not background_tasks:
        raise HTTPException(status_code=500, detail="Background tasks not available")

    background_tasks.add_task(
        KnowledgeBatchService().reindex_embeddings, db=db, batch_size=batch_size
    )

    return {"message": "Reindexing task scheduled"}


# Tag endpoints
@router.post("/tags", response_model=TagInDB)
async def create_tag(
    tag_in: TagCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> TagInDB:
    """Create new tag."""
    tag = await TagService().create_with_validation(
        db, obj_in=tag_in, user_id=current_user["id"]
    )
    return tag


@router.get("/tags", response_model=List[TagInDB])
async def list_tags(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
    skip: int = 0,
    limit: int = 100,
) -> List[TagInDB]:
    """List all tags."""
    return await TagService().get_multi(db, skip=skip, limit=limit)


@router.put("/tags/{tag_id}", response_model=TagInDB)
async def update_tag(
    tag_id: int,
    tag_in: TagUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> TagInDB:
    """Update tag."""
    tag = await TagService().get(db, id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag = await TagService().update_with_validation(
        db, db_obj=tag, obj_in=tag_in, user_id=current_user["id"]
    )
    return tag


@router.delete("/tags/{tag_id}", response_model=TagInDB)
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> TagInDB:
    """Delete tag."""
    tag = await TagService().delete(db, id=tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


# Concept endpoints
@router.post("/concepts", response_model=ConceptInDB)
async def create_concept(
    concept_in: ConceptCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> ConceptInDB:
    """Create new concept."""
    concept = await ConceptService().create_with_validation(
        db, obj_in=concept_in, user_id=current_user["id"]
    )
    return concept


@router.get("/concepts", response_model=List[dict])
async def list_concepts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
    root_id: Optional[int] = None,
) -> List[dict]:
    """List concepts as a hierarchy."""
    return await ConceptService().get_hierarchy(db, root_id=root_id)


@router.put("/concepts/{concept_id}", response_model=ConceptInDB)
async def update_concept(
    concept_id: int,
    concept_in: ConceptUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> ConceptInDB:
    """Update concept."""
    concept = await ConceptService().get(db, id=concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")

    concept = await ConceptService().update_with_validation(
        db, db_obj=concept, obj_in=concept_in, user_id=current_user["id"]
    )
    return concept


@router.delete("/concepts/{concept_id}", response_model=ConceptInDB)
async def delete_concept(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> ConceptInDB:
    """Delete concept."""
    concept = await ConceptService().delete(db, id=concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    return concept


@router.get("/concepts/{concept_id}/ancestors", response_model=List[ConceptInDB])
async def get_concept_ancestors(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> List[ConceptInDB]:
    """Get concept ancestors."""
    return await ConceptService().get_ancestors(db, concept_id=concept_id)


@router.get("/concepts/{concept_id}/descendants", response_model=List[ConceptInDB])
async def get_concept_descendants(
    concept_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    api_key: str = Depends(get_api_key),
) -> List[ConceptInDB]:
    """Get concept descendants."""
    return await ConceptService().get_descendants(db, concept_id=concept_id)
