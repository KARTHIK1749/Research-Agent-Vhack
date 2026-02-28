import { BookOpen, Search, FlaskConical, FileText, CheckCircle, Brain, Database, MessageSquare, ScrollText } from 'lucide-react';

const steps = [
  { id: 'meta', label: 'Meta Agent', icon: Brain },
  { id: 'literature', label: 'Literature', icon: BookOpen },
  { id: 'related_work', label: 'Related Work', icon: ScrollText },
  { id: 'gap', label: 'Gap Detection', icon: Search },
  { id: 'experiment', label: 'Experiment', icon: FlaskConical },
  { id: 'dataset', label: 'Dataset', icon: Database },
  { id: 'draft', label: 'Paper Draft', icon: FileText },
  { id: 'review', label: 'Review', icon: MessageSquare },
];

const Timeline = ({ currentStep }) => {
  const getStepStatus = (stepId) => {
    const stepOrder = ['meta', 'literature', 'related_work', 'gap', 'experiment', 'dataset', 'draft', 'review', 'complete'];
    const currentIdx = stepOrder.indexOf(currentStep);
    const stepIdx = stepOrder.indexOf(stepId);

    if (stepIdx < currentIdx) return 'completed';
    if (stepIdx === currentIdx) return 'current';
    return 'pending';
  };

  return (
    <div className="w-full py-4">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const status = getStepStatus(step.id);
          const Icon = step.icon;

          return (
            <div key={step.id} className="flex items-center flex-1">
              <div className="flex flex-col items-center">
                <div
                  className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-colors ${
                    status === 'completed'
                      ? 'bg-green-500 border-green-500 text-white'
                      : status === 'current'
                      ? 'bg-primary-600 border-primary-600 text-white'
                      : 'bg-white border-gray-300 text-gray-400'
                  }`}
                >
                  {status === 'completed' ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}
                </div>
                <span
                  className={`mt-2 text-xs font-medium ${
                    status === 'pending' ? 'text-gray-400' : 'text-gray-700'
                  }`}
                >
                  {step.label}
                </span>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`flex-1 h-0.5 mx-2 ${
                    status === 'completed' ? 'bg-green-500' : 'bg-gray-200'
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
