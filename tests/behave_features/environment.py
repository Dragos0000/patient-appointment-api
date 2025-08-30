import asyncio
import os
from typing import Any, Coroutine
import httpx
from behave import fixture
from behave.runner import Context


def run_async(context: Context, coro: Coroutine[Any, Any, Any]) -> Any:
    """
    Run an async coroutine in the behave context.
    
    Args:
        context: Behave context object
        coro: Async coroutine to run
        
    Returns:
        Result of the coroutine
    """
    if not hasattr(context, 'loop'):
        context.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(context.loop)
    
    return context.loop.run_until_complete(coro)


@fixture
def api_client(context: Context):
    """
    Create HTTP client for API testing.
    """
    # Get API host from environment or use default
    api_host = os.getenv('API_HOST', '0.0.0.0:8000')
    base_url = f"http://{api_host}"
    
    context.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
    yield context.client
    
    # Cleanup
    run_async(context, context.client.aclose())


def before_all(context: Context):
    """
    Setup before all tests.
    """
    # Initialize async event loop
    context.loop = asyncio.new_event_loop()
    asyncio.set_event_loop(context.loop)
    
    # Setup API client
    api_host = os.getenv('API_HOST', '0.0.0.0:8000')
    base_url = f"http://{api_host}"
    context.client = httpx.AsyncClient(base_url=base_url, timeout=30.0)
    
    # Store created resources for cleanup
    context.created_patients = []
    context.created_appointments = []


def after_all(context: Context):
    """
    Cleanup after all tests.
    """
    # Close HTTP client
    if hasattr(context, 'client'):
        run_async(context, context.client.aclose())
    
    # Close event loop
    if hasattr(context, 'loop'):
        context.loop.close()


def before_scenario(context: Context, scenario):
    """
    Setup before each scenario.
    """
    # Reset scenario-specific data
    context.patient_data = None
    context.appointment_data = None
    context.response = None
    context.created_patient_nhs = None
    context.created_appointment_id = None
    
    # Response storage for different operations
    context.put_appointment_response = None
    context.attend_response = None
    context.reinstate_response = None


def after_scenario(context: Context, scenario):
    """
    Cleanup after each scenario.
    """
    # Clean up created appointments
    if hasattr(context, 'created_appointment_id') and context.created_appointment_id:
        try:
            # Try to delete the appointment (ignore errors if already deleted)
            run_async(context, context.client.delete(f"/appointments/{context.created_appointment_id}"))
        except Exception:
            pass  # Ignore cleanup errors
    
    # Clean up created patients
    if hasattr(context, 'created_patient_nhs') and context.created_patient_nhs:
        try:
            # Try to delete the patient (ignore errors if already deleted)
            run_async(context, context.client.delete(f"/patients/{context.created_patient_nhs}"))
        except Exception:
            pass  # Ignore cleanup errors
