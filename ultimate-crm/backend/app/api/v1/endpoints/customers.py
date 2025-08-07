"""
Customer API endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_session
from app.models.customer import Customer, CustomerSegment
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse, 
    CustomerListResponse, CustomerSegmentResponse
)
from app.services.customer_service import CustomerService
from app.core.exceptions import DataNotFoundException
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/", response_model=CustomerListResponse)
async def list_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    status: Optional[str] = None,
    segment_id: Optional[str] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """
    List customers with pagination and filtering
    """
    try:
        customer_service = CustomerService(db)
        
        filters = {}
        if status:
            filters["status"] = status
        if segment_id:
            filters["segment_id"] = segment_id
        
        customers, total = await customer_service.list_customers(
            skip=skip,
            limit=limit,
            search=search,
            filters=filters
        )
        
        return CustomerListResponse(
            customers=[CustomerResponse.from_orm(customer) for customer in customers],
            total=total,
            skip=skip,
            limit=limit
        )
        
    except Exception as e:
        logger.error("Failed to list customers", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve customers"
        )


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Create a new customer
    """
    try:
        customer_service = CustomerService(db)
        customer = await customer_service.create_customer(customer_data)
        
        logger.info("Customer created", customer_id=str(customer.id), customer_name=customer.name)
        return CustomerResponse.from_orm(customer)
        
    except Exception as e:
        logger.error("Failed to create customer", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create customer"
        )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get customer by ID
    """
    try:
        customer_service = CustomerService(db)
        customer = await customer_service.get_customer(customer_id)
        
        if not customer:
            raise DataNotFoundException("Customer", customer_id)
        
        return CustomerResponse.from_orm(customer)
        
    except DataNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    except Exception as e:
        logger.error("Failed to get customer", customer_id=customer_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve customer"
        )


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: str,
    customer_data: CustomerUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Update customer by ID
    """
    try:
        customer_service = CustomerService(db)
        customer = await customer_service.update_customer(customer_id, customer_data)
        
        if not customer:
            raise DataNotFoundException("Customer", customer_id)
        
        logger.info("Customer updated", customer_id=customer_id)
        return CustomerResponse.from_orm(customer)
        
    except DataNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    except Exception as e:
        logger.error("Failed to update customer", customer_id=customer_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update customer"
        )


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Delete customer by ID
    """
    try:
        customer_service = CustomerService(db)
        success = await customer_service.delete_customer(customer_id)
        
        if not success:
            raise DataNotFoundException("Customer", customer_id)
        
        logger.info("Customer deleted", customer_id=customer_id)
        
    except DataNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    except Exception as e:
        logger.error("Failed to delete customer", customer_id=customer_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete customer"
        )


@router.get("/{customer_id}/health-score")
async def get_customer_health_score(
    customer_id: str,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Get customer health score and metrics
    """
    try:
        customer_service = CustomerService(db)
        health_data = await customer_service.calculate_customer_health(customer_id)
        
        return health_data
        
    except DataNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    except Exception as e:
        logger.error("Failed to calculate customer health", customer_id=customer_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to calculate customer health score"
        )


@router.get("/segments/", response_model=List[CustomerSegmentResponse])
async def list_customer_segments(
    db: AsyncSession = Depends(get_async_session)
):
    """
    List all customer segments
    """
    try:
        customer_service = CustomerService(db)
        segments = await customer_service.list_segments()
        
        return [CustomerSegmentResponse.from_orm(segment) for segment in segments]
        
    except Exception as e:
        logger.error("Failed to list customer segments", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve customer segments"
        )