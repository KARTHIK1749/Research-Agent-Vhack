import { BookOpen, Search, FlaskConical, FileText, CheckCircle, Brain, Database, MessageSquare, ScrollText, Sparkles } from 'lucide-react';

const steps = [
  { id: 'meta', label: 'Meta Agent', icon: Brain, color: 'purple' },
  { id: 'literature', label: 'Literature', icon: BookOpen, color: 'blue' },
  { id: 'related_work', label: 'Related Work', icon: ScrollText, color: 'indigo' },
  { id: 'gap', label: 'Gap Detection', icon: Search, color: 'green' },
  { id: 'experiment', label: 'Experiment', icon: FlaskConical, color: 'orange' },
  { id: 'reflection', label: 'Reflection', icon: Sparkles, color: 'amber' },
  { id: 'dataset', label: 'Dataset', icon: Database, color: 'cyan' },
  { id: 'draft', label: 'Paper Draft', icon: FileText, color: 'pink' },
  { id: 'review', label: 'Review', icon: MessageSquare, color: 'gray' },
];

const Timeline = ({ currentStep }) => {
  const getStepStatus = (stepId) => {
    const stepOrder = ['meta', 'literature', 'related_work', 'gap', 'experiment', 'reflection', 'dataset', 'draft', 'review', 'complete'];
    const currentIdx = stepOrder.indexOf(currentStep);
    const stepIdx = stepOrder.indexOf(stepId);

    if (stepIdx < currentIdx) return 'completed';
    if (stepIdx === currentIdx) return 'current';
    return 'pending';
  };

  const getColorClasses = (color, status) => {
    const colors = {
      purple: {
        completed: 'bg-purple-500 border-purple-500',
        current: 'bg-purple-600 border-purple-600 shadow-lg shadow-purple-200',
        pending: 'bg-white border-gray-300'
      },
      blue: {
        completed: 'bg-blue-500 border-blue-500',
        current: 'bg-blue-600 border-blue-600 shadow-lg shadow-blue-200',
        pending: 'bg-white border-gray-300'
      },
      green: {
        completed: 'bg-green-500 border-green-500',
        current: 'bg-green-600 border-green-600 shadow-lg shadow-green-200',
        pending: 'bg-white border-gray-300'
      },
      orange: {
        completed: 'bg-orange-500 border-orange-500',
        current: 'bg-orange-600 border-orange-600 shadow-lg shadow-orange-200',
        pending: 'bg-white border-gray-300'
      },
      amber: {
        completed: 'bg-amber-500 border-amber-500',
        current: 'bg-amber-600 border-amber-600 shadow-lg shadow-amber-200',
        pending: 'bg-white border-gray-300'
      },
      cyan: {
        completed: 'bg-cyan-500 border-cyan-500',
        current: 'bg-cyan-600 border-cyan-600 shadow-lg shadow-cyan-200',
        pending: 'bg-white border-gray-300'
      },
      indigo: {
        completed: 'bg-indigo-500 border-indigo-500',
        current: 'bg-indigo-600 border-indigo-600 shadow-lg shadow-indigo-200',
        pending: 'bg-white border-gray-300'
      },
      pink: {
        completed: 'bg-pink-500 border-pink-500',
        current: 'bg-pink-600 border-pink-600 shadow-lg shadow-pink-200',
        pending: 'bg-white border-gray-300'
      },
      gray: {
        completed: 'bg-gray-500 border-gray-500',
        current: 'bg-gray-600 border-gray-600 shadow-lg shadow-gray-200',
        pending: 'bg-white border-gray-300'
      }
    };
    
    return colors[color]?.[status] || colors.gray[status];
  };

  return (
    <div className="w-full py-6 overflow-x-auto">
      <div className="flex items-center justify-between min-w-max px-4">
        {steps.map((step, index) => {
          const status = getStepStatus(step.id);
          const Icon = step.icon;

          return (
            <div key={step.id} className="flex items-center flex-1 min-w-0">
              <div className="flex flex-col items-center">
                <div
                  className={`flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all duration-300 transform hover:scale-110 ${
                    status === 'completed'
                      ? `${getColorClasses(step.color, status)} text-white`
                      : status === 'current'
                      ? `${getColorClasses(step.color, status)} text-white animate-pulse`
                      : `${getColorClasses(step.color, status)} text-gray-400`
                  }`}
                >
                  {status === 'completed' ? (
                    <CheckCircle className="w-6 h-6" />
                  ) : (
                    <Icon className="w-6 h-6" />
                  )}
                </div>
                <span
                  className={`mt-3 text-xs font-semibold text-center max-w-20 ${
                    status === 'pending' ? 'text-gray-400' : 
                    status === 'current' ? 'text-gray-900' : 
                    'text-gray-700'
                  }`}
                >
                  {step.label}
                </span>
                {status === 'current' && (
                  <div className="mt-1 w-2 h-2 bg-primary-600 rounded-full animate-ping"></div>
                )}
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`flex-1 h-1 mx-3 rounded-full transition-all duration-500 ${
                    status === 'completed' 
                      ? 'bg-gradient-to-r from-green-400 to-green-500' 
                      : 'bg-gray-200'
                  }`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Timeline;
