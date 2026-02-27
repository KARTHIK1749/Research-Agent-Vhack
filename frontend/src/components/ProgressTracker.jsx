import React, { useState, useEffect } from 'react';
import { CheckCircle2, Circle, AlertCircle, Clock, Loader2, Brain, BookOpen, Link, Search, FlaskConical, RotateCcw, Database, FileText, MessageSquare } from 'lucide-react';

const ProgressTracker = ({ sessionId, isActive }) => {
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Icon mapping for steps
  const stepIcons = {
    meta: Brain,
    literature: BookOpen,
    related_work: Link,
    gap: Search,
    experiment: FlaskConical,
    reflection: RotateCcw,
    dataset: Database,
    draft: FileText,
    review: MessageSquare
  };

  // Status colors
  const statusColors = {
    pending: 'text-gray-400',
    running: 'text-blue-500',
    completed: 'text-green-500',
    failed: 'text-red-500',
    skipped: 'text-gray-400'
  };

  // Background colors
  const statusBgColors = {
    pending: 'bg-gray-100',
    running: 'bg-blue-50',
    completed: 'bg-green-50',
    failed: 'bg-red-50',
    skipped: 'bg-gray-100'
  };

  // Border colors
  const statusBorderColors = {
    pending: 'border-gray-200',
    running: 'border-blue-200',
    completed: 'border-green-200',
    failed: 'border-red-200',
    skipped: 'border-gray-200'
  };

  useEffect(() => {
    if (!sessionId || !isActive) return;

    let intervalId;
    
    const fetchProgress = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://localhost:8000/api/progress/${sessionId}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setProgress(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching progress:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    // Initial fetch
    fetchProgress();

    // Set up polling for real-time updates
    intervalId = setInterval(fetchProgress, 1000); // Poll every second

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [sessionId, isActive]);

  const getStepIcon = (stepName, status) => {
    const IconComponent = stepIcons[stepName] || Circle;
    
    if (status === 'completed') {
      return <CheckCircle2 className="w-5 h-5 text-green-500" />;
    } else if (status === 'running') {
      return <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />;
    } else if (status === 'failed') {
      return <AlertCircle className="w-5 h-5 text-red-500" />;
    } else {
      return <IconComponent className="w-5 h-5 text-gray-400" />;
    }
  };

  const getProgressBarColor = (status) => {
    switch (status) {
      case 'running': return 'bg-blue-500';
      case 'completed': return 'bg-green-500';
      case 'failed': return 'bg-red-500';
      default: return 'bg-gray-300';
    }
  };

  if (!isActive) {
    return null;
  }

  if (loading && !progress) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-center">
          <Loader2 className="w-6 h-6 text-blue-500 animate-spin mr-2" />
          <span className="text-gray-600">Loading progress...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg border border-red-200 p-6">
        <div className="flex items-center text-red-600">
          <AlertCircle className="w-5 h-5 mr-2" />
          <span>Error loading progress: {error}</span>
        </div>
      </div>
    );
  }

  if (!progress) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      {/* Overall Progress */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-800">Research Progress</h3>
          <span className="text-sm text-gray-600">
            {progress.completed_steps}/{progress.total_steps} steps completed
          </span>
        </div>
        
        {/* Overall Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className="bg-blue-500 h-3 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progress.overall_progress}%` }}
          />
        </div>
        
        <div className="flex justify-between mt-1">
          <span className="text-xs text-gray-500">
            {progress.overall_progress.toFixed(1)}% Complete
          </span>
          {progress.current_step && (
            <span className="text-xs text-blue-600 font-medium">
              Currently: {progress.steps[progress.current_step]?.display_name || progress.current_step}
            </span>
          )}
        </div>
      </div>

      {/* Individual Steps */}
      <div className="space-y-3">
        {Object.entries(progress.steps).map(([stepKey, step]) => (
          <div 
            key={stepKey}
            className={`border rounded-lg p-4 transition-all duration-200 ${
              statusBorderColors[step.status]
            } ${statusBgColors[step.status]}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3 flex-1">
                {/* Step Icon */}
                <div className="mt-0.5">
                  {getStepIcon(stepKey, step.status)}
                </div>
                
                {/* Step Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className={`font-medium ${
                      step.status === 'running' ? 'text-blue-700' : 
                      step.status === 'completed' ? 'text-green-700' : 
                      step.status === 'failed' ? 'text-red-700' : 'text-gray-600'
                    }`}>
                      {step.display_name}
                    </h4>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      step.status === 'running' ? 'bg-blue-100 text-blue-700' :
                      step.status === 'completed' ? 'bg-green-100 text-green-700' :
                      step.status === 'failed' ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-600'
                    }`}>
                      {step.status.charAt(0).toUpperCase() + step.status.slice(1)}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-2">{step.description}</p>
                  
                  {/* Current Operation */}
                  {step.current_operation && step.status !== 'completed' && (
                    <div className="flex items-center text-sm text-gray-500 mb-2">
                      {step.status === 'running' && (
                        <Loader2 className="w-3 h-3 mr-1 animate-spin" />
                      )}
                      <span>{step.current_operation}</span>
                    </div>
                  )}
                  
                  {/* Progress Bar for Running Steps */}
                  {step.status === 'running' && step.progress_percentage > 0 && (
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                      <div 
                        className={`h-2 rounded-full transition-all duration-300 ease-out ${getProgressBarColor(step.status)}`}
                        style={{ width: `${step.progress_percentage}%` }}
                      />
                    </div>
                  )}
                  
                  {/* Error Message */}
                  {step.error_message && (
                    <div className="text-sm text-red-600 bg-red-50 p-2 rounded border border-red-200">
                      <strong>Error:</strong> {step.error_message}
                    </div>
                  )}
                  
                  {/* Step Details */}
                  {step.details && Object.keys(step.details).length > 0 && (
                    <div className="text-xs text-gray-500 mt-2">
                      {Object.entries(step.details).map(([key, value]) => (
                        <div key={key} className="flex justify-between">
                          <span className="capitalize">{key.replace('_', ' ')}:</span>
                          <span className="font-medium">
                            {typeof value === 'number' ? value.toLocaleString() : value}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {/* Duration */}
                  {step.duration && (
                    <div className="text-xs text-gray-500 mt-1">
                      Duration: {step.duration.toFixed(2)}s
                    </div>
                  )}
                </div>
              </div>
              
              {/* Step Icon (decorative) */}
              <div className={`text-2xl ml-2 ${statusColors[step.status]}`}>
                {step.icon}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-4 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-green-600">{progress.completed_steps}</div>
            <div className="text-xs text-gray-600">Completed</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-blue-600">{progress.running_steps}</div>
            <div className="text-xs text-gray-600">Running</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-red-600">{progress.failed_steps}</div>
            <div className="text-xs text-gray-600">Failed</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-600">{progress.total_steps}</div>
            <div className="text-xs text-gray-600">Total Steps</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressTracker;
