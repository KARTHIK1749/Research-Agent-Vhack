import { useState } from 'react';
import { Sparkles, Loader2, ArrowRight, RotateCcw, Brain } from 'lucide-react';
import ChatInput from '../components/ChatInput';
import Timeline from '../components/Timeline';
import AgentOutputCard from '../components/AgentOutputCard';
import { startResearch, executeStep } from '../services/api';

const Home = () => {
  const [sessionId, setSessionId] = useState(null);
  const [researchGoal, setResearchGoal] = useState('');
  const [currentStep, setCurrentStep] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [outputs, setOutputs] = useState({});
  const [selectedGap, setSelectedGap] = useState(0);
  const [error, setError] = useState(null);

  const handleStartResearch = async (goal) => {
    setIsLoading(true);
    setError(null);
    setResearchGoal(goal);

    try {
      const response = await startResearch(goal);
      setSessionId(response.session_id);
      setCurrentStep('gap');
      setOutputs({
        meta: {
          optimized_query: response.state.meta_optimization?.optimized_query,
          query_rationale: response.state.meta_optimization?.query_rationale,
        },
        literature: {
          papers: response.state.papers,
          literature_summary: response.state.literature_summary,
        },
      });
    } catch (err) {
      setError('Failed to start research. Please check your API keys and try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNextStep = async () => {
    if (!sessionId) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await executeStep(sessionId, selectedGap);
      const { state, step_completed, next_step, output } = response;

      setCurrentStep(next_step || 'complete');

      // Accumulate outputs
      setOutputs((prev) => ({
        ...prev,
        [step_completed]: output,
      }));
    } catch (err) {
      setError('Failed to execute step. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSessionId(null);
    setResearchGoal('');
    setCurrentStep(null);
    setOutputs({});
    setSelectedGap(0);
    setError(null);
  };

  const renderStepContent = () => {
    if (!currentStep) {
      return (
        <div className="text-center py-12">
          <Sparkles className="w-12 h-12 text-primary-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Welcome to AI Research Co-Scientist
          </h2>
          <p className="text-gray-600 max-w-md mx-auto">
            Enter your research goal above to start an AI-powered research workflow.
            We'll help you discover papers, identify gaps, design experiments, and draft your paper.
          </p>
        </div>
      );
    }

    return (
      <div className="space-y-6">
        <Timeline currentStep={currentStep} />

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Meta Agent Output */}
        {outputs.meta && (
          <AgentOutputCard
            step="meta"
            title="Meta Agent / Research Director"
            data={outputs.meta}
            isActive={currentStep === 'literature'}
          />
        )}

        {/* Literature Output */}
        {outputs.literature && (
          <AgentOutputCard
            step="literature"
            title="Literature Review"
            data={outputs.literature}
            isActive={currentStep === 'gap'}
          />
        )}

        {/* Gap Selection */}
        {currentStep === 'gap' && outputs.literature && (
          <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <p className="text-sm text-gray-700 mb-3">
              Select a research gap to pursue (we'll default to Gap 0):
            </p>
            <select
              value={selectedGap}
              onChange={(e) => setSelectedGap(Number(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {[0, 1, 2, 3, 4].map((i) => (
                <option key={i} value={i}>Gap {i}</option>
              ))}
            </select>
          </div>
        )}

        {/* Related Work Output */}
        {outputs.related_work && (
          <AgentOutputCard
            step="related_work"
            title="Related Work Section"
            data={outputs.related_work}
            isActive={currentStep === 'gap'}
          />
        )}

        {/* Gap Output */}
        {outputs.gap && (
          <AgentOutputCard
            step="gap"
            title="Research Gaps Identified"
            data={outputs.gap}
            isActive={currentStep === 'experiment'}
          />
        )}

        {/* Experiment Output */}
        {outputs.experiment && (
          <AgentOutputCard
            step="experiment"
            title="Experiment Design"
            data={outputs.experiment}
            isActive={currentStep === 'dataset'}
          />
        )}

        {/* Dataset Recommendation Output */}
        {outputs.dataset && (
          <AgentOutputCard
            step="dataset"
            title="Dataset Recommendation"
            data={outputs.dataset}
            isActive={currentStep === 'draft'}
          />
        )}

        {/* Draft Output */}
        {outputs.draft && (
          <AgentOutputCard
            step="draft"
            title="Paper Draft"
            data={outputs.draft}
            isActive={currentStep === 'review'}
          />
        )}

        {/* Review Output */}
        {outputs.review && (
          <AgentOutputCard
            step="review"
            title="Peer Review Simulation"
            data={outputs.review}
            isActive={currentStep === 'complete'}
          />
        )}

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4 pt-4">
          {currentStep !== 'complete' && (
            <button
              onClick={handleNextStep}
              disabled={isLoading}
              className="flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  {currentStep === 'gap' && 'Find Gaps'}
                  {currentStep === 'experiment' && 'Design Experiment'}
                  {currentStep === 'dataset' && 'Recommend Dataset'}
                  {currentStep === 'draft' && 'Generate Draft'}
                  {currentStep === 'review' && 'Simulate Review'}
                  {currentStep === 'related_work' && 'Write Related Work'}
                  {currentStep === 'literature' && 'Next: Literature'}
                  <ArrowRight className="w-5 h-5 ml-2" />
                </>
              )}
            </button>
          )}

          {currentStep === 'complete' && (
            <button
              onClick={handleReset}
              className="flex items-center px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              <RotateCcw className="w-5 h-5 mr-2" />
              Start New Research
            </button>
          )}
        </div>

        {currentStep === 'complete' && (
          <div className="text-center p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800 font-medium">
              Research workflow complete! Review your draft above.
            </p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-6 h-6 text-primary-600" />
            <h1 className="text-xl font-bold text-gray-900">AI Research Co-Scientist</h1>
          </div>
          {sessionId && (
            <button
              onClick={handleReset}
              className="text-sm text-gray-500 hover:text-gray-700"
            >
              New Session
            </button>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Input Section */}
        <div className="mb-8">
          <ChatInput
            onSubmit={handleStartResearch}
            isLoading={isLoading && !sessionId}
            placeholder="Enter your research goal (e.g., 'Improving transformer efficiency for long sequences')..."
          />
        </div>

        {/* Research Goal Display */}
        {researchGoal && (
          <div className="mb-6 p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
            <p className="text-sm text-gray-500">Research Goal:</p>
            <p className="text-lg font-medium text-gray-900">{researchGoal}</p>
          </div>
        )}

        {/* Step Content */}
        {renderStepContent()}
      </main>
    </div>
  );
};

export default Home;
