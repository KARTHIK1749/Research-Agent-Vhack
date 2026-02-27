import { useState } from 'react';
import { Sparkles, Loader2, ArrowRight, RotateCcw, Brain, BarChart3, Target, Lightbulb, TrendingUp, Zap } from 'lucide-react';
import ChatInput from '../components/ChatInput';
import Timeline from '../components/Timeline';
import AgentOutputCard from '../components/AgentOutputCard';
import RISCard from '../components/RISCard';
import ProgressTracker from '../components/ProgressTracker';
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
          cluster_analysis: response.state.cluster_analysis,
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
          {/* <Sparkles className="w-12 h-12 text-primary-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            
          </h2>
          <p className="text-gray-600 max-w-md mx-auto">
            
          </p> */}
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
            isActive={currentStep === 'reflection'}
          />
        )}

        {/* RIS Analysis */}
        {(outputs.experiment?.research_scores || outputs.refined_output || outputs.literature?.cluster_analysis) && (
          <RISCard
            researchScores={outputs.experiment?.research_scores}
            refinedOutput={outputs.refined_output}
            clusterAnalysis={outputs.literature?.cluster_analysis}
          />
        )}

        {/* Reflection Output */}
        {outputs.refined_output && (
          <AgentOutputCard
            step="reflection"
            title="Hypothesis Refinement"
            data={outputs.refined_output}
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
              className="flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-3 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  {currentStep === 'gap' && 'Find Gaps'}
                  {currentStep === 'experiment' && 'Design Experiment'}
                  {currentStep === 'reflection' && 'Refine Hypothesis'}
                  {currentStep === 'dataset' && 'Recommend Dataset'}
                  {currentStep === 'draft' && 'Generate Draft'}
                  {currentStep === 'review' && 'Simulate Review'}
                  {currentStep === 'related_work' && 'Write Related Work'}
                  {currentStep === 'literature' && 'Next: Literature'}
                  <ArrowRight className="w-5 h-5 ml-3" />
                </>
              )}
            </button>
          )}

          {currentStep === 'complete' && (
            <button
              onClick={handleReset}
              className="flex items-center px-8 py-4 bg-gradient-to-r from-gray-600 to-gray-700 text-white rounded-xl hover:from-gray-700 hover:to-gray-800 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              <RotateCcw className="w-5 h-5 mr-3" />
              Start New Research
            </button>
          )}
        </div>

        {currentStep === 'complete' && (
          <div className="text-center p-6 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl shadow-md">
            <div className="flex items-center justify-center mb-2">
              <Zap className="w-6 h-6 text-green-600 mr-2" />
              <p className="text-green-800 font-semibold text-lg">
                Research workflow complete! 
              </p>
            </div>
            <p className="text-green-700">
              Review your comprehensive research draft with RIS analysis above.
            </p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg">
              <Brain className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">MARIS</h1>
              <p className="text-xs text-gray-500">Multi-Agent Research Intelligence System</p>
            </div>
          </div>
          {sessionId && (
            <button
              onClick={handleReset}
              className="flex items-center px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <RotateCcw className="w-4 h-4 mr-2" />
              New Session
            </button>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Hero Section */}
        {!sessionId && (
          <div className="text-center mb-12">
            <div className="flex justify-center mb-6">
              <div className="p-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-xl">
                <Brain className="w-12 h-12 text-white" />
              </div>
            </div>
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              AI-Powered Research Intelligence
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-8">
              Transform your research ideas into comprehensive paper drafts with advanced AI agents, 
              analytical gap detection, and research intelligence scoring.
            </p>
            
            {/* Feature Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-12">
              <div className="p-6 bg-white rounded-xl shadow-md border border-gray-100">
                <BarChart3 className="w-8 h-8 text-blue-600 mb-3 mx-auto" />
                <h3 className="font-semibold text-gray-900 mb-2">Analytical Gap Engine</h3>
                <p className="text-sm text-gray-600">KMeans clustering identifies sparsest research areas</p>
              </div>
              <div className="p-6 bg-white rounded-xl shadow-md border border-gray-100">
                <Target className="w-8 h-8 text-purple-600 mb-3 mx-auto" />
                <h3 className="font-semibold text-gray-900 mb-2">Research Intelligence Score</h3>
                <p className="text-sm text-gray-600">Quantitative assessment of novelty, feasibility, and impact</p>
              </div>
              <div className="p-6 bg-white rounded-xl shadow-md border border-gray-100">
                <Lightbulb className="w-8 h-8 text-amber-600 mb-3 mx-auto" />
                <h3 className="font-semibold text-gray-900 mb-2">Self-Reflection Loop</h3>
                <p className="text-sm text-gray-600">AI-powered hypothesis refinement and improvement</p>
              </div>
            </div>
          </div>
        )}

        {/* Input Section */}
        <div className="mb-8">
          <ChatInput
            onSubmit={handleStartResearch}
            isLoading={isLoading && !sessionId}
            placeholder="Enter your research goal (e.g., 'Improving transformer efficiency for long sequences')..."
          />
        </div>

        {/* Current Research Goal */}
        {sessionId && researchGoal && (
          <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm font-medium text-blue-800 mb-1">Current Research Goal:</p>
            <p className="text-lg font-semibold text-blue-900">{researchGoal}</p>
          </div>
        )}

        {/* Progress Tracker */}
        {sessionId && (
          <div className="mb-8">
            <ProgressTracker sessionId={sessionId} isActive={true} />
          </div>
        )}

        {/* Step Content */}
        {renderStepContent()}
      </main>
    </div>
  );
};

export default Home;
