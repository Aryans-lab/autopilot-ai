"""
Parallel Execution Engine - Massively Parallel Task Processing

NanoCorp can now execute thousands of tasks in parallel,
making it exponentially faster at accomplishing goals.
"""
import asyncio
import concurrent.futures
import time
import uuid
from typing import Dict, Any, List, Optional, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict
import heapq


class ExecutionMode(str, Enum):
    """Task execution modes"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    PIPELINE = "pipeline"
    DAG = "dag"  # Directed Acyclic Graph


class TaskPriority(int, Enum):
    """Task priorities (lower is higher priority)"""
    CRITICAL = 1
    URGENT = 2
    HIGH = 3
    NORMAL = 5
    LOW = 7
    BACKLOG = 10


@dataclass
class TaskResult:
    """Result of a task execution"""
    task_id: str
    success: bool
    output: Any
    error: Optional[str] = None
    duration: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    worker: Optional[str] = None


@dataclass
class ExecutionNode:
    """A node in the execution graph"""
    id: str
    task_id: str
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, ready, running, completed, failed
    result: Optional[TaskResult] = None
    priority: int = 5


class ParallelExecutor:
    """
    Parallel Execution Engine
    
    Features:
    - Task pipelining and parallelization
    - Dependency management (DAG execution)
    - Dynamic load balancing
    - Priority queue scheduling
    - Async/concurrent execution
    - Batch processing
    - Resource pooling
    """
    
    def __init__(
        self,
        max_workers: int = 10,
        mode: ExecutionMode = ExecutionMode.PARALLEL
    ):
        self.max_workers = max_workers
        self.mode = mode
        
        # Execution state
        self.execution_graph: Dict[str, ExecutionNode] = {}
        self.task_queue: List[Tuple[int, str]] = []  # Priority queue
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        
        # Metrics
        self.metrics = {
            "total_executed": 0,
            "total_succeeded": 0,
            "total_failed": 0,
            "total_duration": 0.0,
            "avg_duration": 0.0,
            "peak_concurrency": 0,
            "current_concurrency": 0
        }
        
        # Workers pool
        self.workers: Dict[str, Callable] = {}
        self.worker_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "tasks_completed": 0,
            "total_duration": 0.0,
            "success_rate": 1.0
        })
    
    def register_worker(self, name: str, worker_fn: Callable):
        """Register a worker function"""
        self.workers[name] = worker_fn
    
    def submit_task(
        self,
        task_id: str,
        worker_name: str,
        params: Dict[str, Any],
        priority: int = 5,
        dependencies: Optional[List[str]] = None
    ) -> str:
        """Submit a task for execution"""
        node = ExecutionNode(
            id=f"node_{task_id}",
            task_id=task_id,
            dependencies=dependencies or [],
            priority=priority
        )
        
        # Update dependency graph
        self.execution_graph[node.id] = node
        for dep_id in node.dependencies:
            if dep_id in self.execution_graph:
                self.execution_graph[dep_id].dependents.append(node.id)
        
        # Add to priority queue if ready
        if self._is_ready(node):
            heapq.heappush(self.task_queue, (priority, node.id))
            node.status = "ready"
        
        return node.id
    
    def submit_batch(
        self,
        tasks: List[Dict[str, Any]],
        batch_priority: int = 5
    ) -> List[str]:
        """Submit a batch of tasks"""
        node_ids = []
        
        for task in tasks:
            node_id = self.submit_task(
                task_id=task["id"],
                worker_name=task["worker"],
                params=task.get("params", {}),
                priority=task.get("priority", batch_priority),
                dependencies=task.get("dependencies")
            )
            node_ids.append(node_id)
        
        return node_ids
    
    def _is_ready(self, node: ExecutionNode) -> bool:
        """Check if a node is ready to execute"""
        if node.dependencies:
            for dep_id in node.dependencies:
                dep_node = self.execution_graph.get(dep_id)
                if not dep_node or dep_node.status != "completed":
                    return False
        return True
    
    async def execute_async(
        self,
        task_id: str,
        worker_name: str,
        params: Dict[str, Any],
        timeout: Optional[float] = None
    ) -> TaskResult:
        """Execute a task asynchronously"""
        task_id_str = f"task_{task_id}_{int(time.time())}"
        start_time = datetime.now()
        
        try:
            worker = self.workers.get(worker_name)
            if not worker:
                return TaskResult(
                    task_id=task_id,
                    success=False,
                    output=None,
                    error=f"Worker '{worker_name}' not found",
                    duration=0.0,
                    started_at=start_time,
                    completed_at=datetime.now()
                )
            
            # Execute with optional timeout
            if asyncio.iscoroutinefunction(worker):
                if timeout:
                    result = await asyncio.wait_for(
                        worker(**params),
                        timeout=timeout
                    )
                else:
                    result = await worker(**params)
            else:
                # Run sync function in executor
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: worker(**params)
                )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return TaskResult(
                task_id=task_id,
                success=True,
                output=result,
                duration=duration,
                started_at=start_time,
                completed_at=datetime.now(),
                worker=worker_name
            )
            
        except asyncio.TimeoutError:
            return TaskResult(
                task_id=task_id,
                success=False,
                output=None,
                error="Task timed out",
                duration=timeout or 0.0,
                started_at=start_time,
                completed_at=datetime.now()
            )
        except Exception as e:
            return TaskResult(
                task_id=task_id,
                success=False,
                output=None,
                error=str(e),
                duration=(datetime.now() - start_time).total_seconds(),
                started_at=start_time,
                completed_at=datetime.now()
            )
    
    def execute_parallel(
        self,
        max_concurrent: Optional[int] = None
    ) -> List[TaskResult]:
        """Execute all ready tasks in parallel"""
        if max_concurrent is None:
            max_concurrent = self.max_workers
        
        results = []
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def run_with_semaphore(task_id: str, node_id: str):
            async with semaphore:
                node = self.execution_graph.get(node_id)
                if node:
                    node.status = "running"
                    self.metrics["current_concurrency"] += 1
                    self.metrics["peak_concurrency"] = max(
                        self.metrics["peak_concurrency"],
                        self.metrics["current_concurrency"]
                    )
                    
                    result = await self.execute_async(
                        task_id=node.task_id,
                        worker_name=node.task_id.split(":")[0] if ":" in node.task_id else "default",
                        params={}
                    )
                    
                    node.result = result
                    node.status = "completed" if result.success else "failed"
                    self.completed_tasks[node.id] = result
                    
                    self.metrics["current_concurrency"] -= 1
                    self.metrics["total_executed"] += 1
                    
                    if result.success:
                        self.metrics["total_succeeded"] += 1
                    else:
                        self.metrics["total_failed"] += 1
                    
                    self.metrics["total_duration"] += result.duration
                    self.metrics["avg_duration"] = (
                        self.metrics["total_duration"] / self.metrics["total_executed"]
                    )
                    
                    # Update worker stats
                    if result.worker:
                        self.worker_stats[result.worker]["tasks_completed"] += 1
                        self.worker_stats[result.worker]["total_duration"] += result.duration
                    
                    # Check dependents and add to queue if ready
                    for dep_id in node.dependents:
                        dep_node = self.execution_graph.get(dep_id)
                        if dep_node and self._is_ready(dep_node):
                            heapq.heappush(
                                self.task_queue,
                                (dep_node.priority, dep_node.id)
                            )
                            dep_node.status = "ready"
                    
                    return result
                return None
        
        # Run all tasks
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Execute while there are tasks in queue
            while self.task_queue:
                # Get batch of ready tasks
                batch = []
                while self.task_queue and len(batch) < max_concurrent:
                    _, node_id = heapq.heappop(self.task_queue)
                    batch.append(run_with_semaphore(None, node_id))
                
                if batch:
                    batch_results = loop.run_until_complete(
                        asyncio.gather(*batch, return_exceptions=True)
                    )
                    results.extend([r for r in batch_results if r])
        finally:
            loop.close()
        
        return results
    
    def execute_pipeline(
        self,
        pipeline: List[Dict[str, Any]],
        data: Any
    ) -> List[Any]:
        """Execute a pipeline of tasks"""
        results = [data]
        
        for stage in pipeline:
            worker_name = stage.get("worker", "default")
            transform_fn = stage.get("transform", lambda x: x)
            
            worker = self.workers.get(worker_name)
            if worker:
                if asyncio.iscoroutinefunction(worker):
                    loop = asyncio.new_event_loop()
                    result = loop.run_until_complete(worker(data))
                    loop.close()
                else:
                    result = worker(data)
                
                if stage.get("map", False):
                    # Map over results
                    new_results = []
                    for r in results:
                        new_results.append(transform_fn(r))
                    results = new_results
                else:
                    results = [transform_fn(r) for r in results]
        
        return results
    
    def execute_dag(
        self,
        dag: Dict[str, List[str]],  # task_id -> dependencies
        executor_fn: Callable
    ) -> Dict[str, TaskResult]:
        """Execute a DAG of tasks"""
        results = {}
        
        # Build execution graph
        self.execution_graph.clear()
        for task_id, deps in dag.items():
            node_id = f"node_{task_id}"
            self.execution_graph[node_id] = ExecutionNode(
                id=node_id,
                task_id=task_id,
                dependencies=[f"node_{d}" for d in deps],
                priority=5
            )
        
        # Add initial nodes with no dependencies
        for node_id, node in self.execution_graph.items():
            if not node.dependencies:
                heapq.heappush(self.task_queue, (node.priority, node_id))
                node.status = "ready"
        
        # Execute
        while self.task_queue:
            _, node_id = heapq.heappop(self.task_queue)
            node = self.execution_graph[node_id]
            
            if node.status == "ready":
                result = loop.run_until_complete(
                    self.execute_async(node.task_id, "default", {})
                ) if not asyncio.get_event_loop().is_running() else None
                
                node.result = result
                node.status = "completed" if result.success else "failed"
                results[node.task_id] = result
                
                # Unlock dependents
                for dep_id in node.dependents:
                    dep_node = self.execution_graph.get(dep_id)
                    if dep_node and self._is_ready(dep_node):
                        heapq.heappush(self.task_queue, (dep_node.priority, dep_id))
                        dep_node.status = "ready"
        
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get execution metrics"""
        return {
            **self.metrics,
            "workers": list(self.workers.keys()),
            "worker_stats": dict(self.worker_stats),
            "queue_length": len(self.task_queue),
            "running_tasks": len(self.running_tasks),
            "completed_tasks": len(self.completed_tasks)
        }
    
    def get_execution_graph(self) -> Dict[str, Any]:
        """Get current execution graph state"""
        return {
            node_id: {
                "task_id": node.task_id,
                "status": node.status,
                "dependencies": node.dependencies,
                "completed": node.result.success if node.result else None
            }
            for node_id, node in self.execution_graph.items()
        }


class AdaptiveExecutor(ParallelExecutor):
    """
    Adaptive Parallel Executor
    
    Automatically adjusts parallelism based on:
    - Worker performance
    - Task complexity
    - System resources
    - Success rates
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.adaptation_interval = 60  # seconds
        self.last_adaptation = datetime.now()
        self.target_success_rate = 0.95
    
    def auto_scale(self):
        """Automatically scale workers based on performance"""
        now = datetime.now()
        
        if (now - self.last_adaptation).total_seconds() < self.adaptation_interval:
            return
        
        # Calculate success rate
        if self.metrics["total_executed"] > 0:
            success_rate = self.metrics["total_succeeded"] / self.metrics["total_executed"]
        else:
            success_rate = 1.0
        
        # Adjust concurrency
        if success_rate >= self.target_success_rate:
            # Increase parallelism
            new_workers = min(self.max_workers * 2, 100)
            if new_workers > self.max_workers:
                self.max_workers = new_workers
        else:
            # Decrease parallelism
            self.max_workers = max(1, self.max_workers // 2)
        
        self.last_adaptation = now
    
    def select_best_worker(self, task_type: str) -> str:
        """Select the best worker for a task type"""
        best_worker = None
        best_score = -1
        
        for worker_name, stats in self.worker_stats.items():
            if stats["tasks_completed"] == 0:
                continue
            
            avg_duration = stats["total_duration"] / stats["tasks_completed"]
            success_rate = stats["success_rate"]
            
            # Score = success_rate / (1 + avg_duration)
            score = success_rate / (1 + avg_duration)
            
            if score > best_score:
                best_score = score
                best_worker = worker_name
        
        return best_worker or list(self.workers.keys())[0] if self.workers else "default"


class BatchProcessor:
    """
    Batch Processor for handling large volumes of similar tasks
    """
    
    def __init__(
        self,
        batch_size: int = 100,
        executor: Optional[ParallelExecutor] = None
    ):
        self.batch_size = batch_size
        self.executor = executor or ParallelExecutor()
        self.pending_batches: List[List[Dict[str, Any]]] = []
        self.completed_batches: List[Dict[str, Any]] = []
    
    def add_to_batch(self, task: Dict[str, Any]):
        """Add a task to the current batch"""
        if not self.pending_batches:
            self.pending_batches.append([])
        
        current_batch = self.pending_batches[-1]
        
        if len(current_batch) >= self.batch_size:
            self.pending_batches.append([])
            current_batch = self.pending_batches[-1]
        
        current_batch.append(task)
    
    def process_batch(
        self,
        worker_name: str,
        transform_fn: Optional[Callable] = None
    ) -> List[TaskResult]:
        """Process current batch"""
        if not self.pending_batches:
            return []
        
        batch = self.pending_batches.pop(0)
        
        if transform_fn:
            # Map transform over batch
            for task in batch:
                task["params"] = transform_fn(task.get("params", {}))
        
        # Submit and execute
        node_ids = self.executor.submit_batch(batch)
        results = self.executor.execute_parallel()
        
        self.completed_batches.append({
            "batch_id": len(self.completed_batches),
            "size": len(batch),
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
        return results
    
    def process_all_batches(
        self,
        worker_name: str,
        transform_fn: Optional[Callable] = None
    ) -> List[TaskResult]:
        """Process all pending batches"""
        all_results = []
        
        while self.pending_batches:
            results = self.process_batch(worker_name, transform_fn)
            all_results.extend(results)
        
        return all_results
