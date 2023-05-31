"""Exceptions for taskerapi"""
class TaskerError(Exception):
    """Base exception for taskerapi"""
    
class TaskerAuthError(TaskerError):
    """Represent Tasker authorization errors"""
