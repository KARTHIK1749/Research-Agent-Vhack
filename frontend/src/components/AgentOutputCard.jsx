import { useState } from 'react';
import { ChevronDown, ChevronUp, BookOpen, Search, FlaskConical, FileText, ExternalLink, Brain, Database, MessageSquare } from 'lucide-react';

const AgentOutputCard = ({ step, title, data, isActive }) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const stepConfig = {
    meta: {
      icon: Brain,
      color: 'bg-indigo-600',
      lightColor: 'bg-indigo-50',
      borderColor: 'border-indigo-200',
    },
    literature: {
      icon: BookOpen,
      color: 'bg-blue-500',
      lightColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
    },
    related_work: {
      icon: BookOpen,
      color: 'bg-amber-500',
      lightColor: 'bg-amber-50',
      borderColor: 'border-amber-200',
    },
    gap: {
      icon: Search,
      color: 'bg-purple-500',
      lightColor: 'bg-purple-50',
      borderColor: 'border-purple-200',
    },
    experiment: {
      icon: FlaskConical,
      color: 'bg-orange-500',
      lightColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
    },
    dataset: {
      icon: Database,
      color: 'bg-teal-500',
      lightColor: 'bg-teal-50',
      borderColor: 'border-teal-200',
    },
    draft: {
      icon: FileText,
      color: 'bg-green-500',
      lightColor: 'bg-green-50',
      borderColor: 'border-green-200',
    },
    review: {
      icon: MessageSquare,
      color: 'bg-gray-600',
      lightColor: 'bg-gray-50',
      borderColor: 'border-gray-200',
    },
  };

  const config = stepConfig[step] || stepConfig.literature;
  const Icon = config.icon;

  const renderContent = () => {
    if (!data) return <p className="text-gray-500 italic">No data available</p>;

    switch (step) {
      case 'meta':
        return (
          <div className="space-y-4">
            <div className="p-4 bg-indigo-50 rounded border border-indigo-200">
              <h4 className="font-semibold text-indigo-800 mb-2">Query Optimization</h4>
              <p className="text-sm text-gray-700 mb-2">
                <strong>Optimized Query:</strong> {data.optimized_query || 'N/A'}
              </p>
              <p className="text-sm text-gray-600">
                <strong>Rationale:</strong> {data.query_rationale || 'N/A'}
              </p>
            </div>
            {data.auto_selection_reasoning && (
              <div className="p-3 bg-white rounded border border-gray-200">
                <h4 className="font-medium text-gray-700 text-sm mb-1">Gap Selection</h4>
                <p className="text-sm text-gray-600">{data.auto_selection_reasoning}</p>
              </div>
            )}
          </div>
        );

      case 'literature':
        return (
          <div className="space-y-4">
            {data.papers?.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">Retrieved Papers ({data.papers.length})</h4>
                <div className="space-y-2 max-h-60 overflow-y-auto">
                  {data.papers.slice(0, 5).map((paper, idx) => (
                    <div key={idx} className="p-3 bg-white rounded border border-gray-200">
                      <p className="font-medium text-sm text-gray-900">{paper.title}</p>
                      <p className="text-xs text-gray-500 mt-1">{paper.authors?.slice(0, 3).join(', ')}...</p>
                      {paper.pdf_url && (
                        <a href={paper.pdf_url} target="_blank" rel="noopener noreferrer" className="text-xs text-primary-600 hover:underline inline-flex items-center mt-1">
                          View PDF <ExternalLink className="w-3 h-3 ml-1" />
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {data.literature_summary && (
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">Analysis Summary</h4>
                <div className="p-3 bg-white rounded border border-gray-200 text-sm text-gray-700 whitespace-pre-wrap">
                  {data.literature_summary}
                </div>
              </div>
            )}
          </div>
        );

      case 'gap':
        return (
          <div className="space-y-3">
            {data.gaps?.map((gap, idx) => (
              <div key={idx} className="p-4 bg-white rounded border border-gray-200">
                <div className="flex items-start justify-between">
                  <h4 className="font-semibold text-gray-800">Gap {idx + 1}</h4>
                  <span className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded">#{idx}</span>
                </div>
                <p className="text-sm text-gray-700 mt-2"><strong>Description:</strong> {gap.description}</p>
                <p className="text-sm text-gray-600 mt-1"><strong>Rationale:</strong> {gap.rationale}</p>
                <p className="text-sm text-gray-600 mt-1"><strong>Impact:</strong> {gap.impact}</p>
              </div>
            ))}
          </div>
        );

      case 'experiment':
        const exp = data.experiment;
        if (!exp) return <p className="text-gray-500">No experiment data</p>;
        return (
          <div className="space-y-4">
            <div className="p-4 bg-orange-50 rounded border border-orange-200">
              <h4 className="font-semibold text-orange-800 mb-2">Hypothesis</h4>
              <p className="text-sm text-gray-700">{exp.hypothesis}</p>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-white rounded border border-gray-200">
                <h4 className="font-medium text-gray-700 text-sm">Dataset</h4>
                <p className="text-sm text-gray-600 mt-1">{exp.dataset_suggestion}</p>
              </div>
              <div className="p-3 bg-white rounded border border-gray-200">
                <h4 className="font-medium text-gray-700 text-sm">Proposed Method</h4>
                <p className="text-sm text-gray-600 mt-1">{exp.proposed_method}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-white rounded border border-gray-200">
                <h4 className="font-medium text-gray-700 text-sm">Metrics</h4>
                <ul className="mt-1 space-y-1">
                  {exp.metrics?.map((metric, idx) => (
                    <li key={idx} className="text-sm text-gray-600">• {metric}</li>
                  ))}
                </ul>
              </div>
              <div className="p-3 bg-white rounded border border-gray-200">
                <h4 className="font-medium text-gray-700 text-sm">Baseline Methods</h4>
                <ul className="mt-1 space-y-1">
                  {exp.baseline_methods?.map((method, idx) => (
                    <li key={idx} className="text-sm text-gray-600">• {method}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        );

      case 'draft':
        const draft = data.draft;
        if (!draft) return <p className="text-gray-500">No draft data</p>;
        return (
          <div className="space-y-4">
            <div className="p-4 bg-green-50 rounded border border-green-200">
              <h4 className="font-semibold text-green-800 text-lg">{draft.title}</h4>
            </div>
            <div className="p-4 bg-white rounded border border-gray-200">
              <h4 className="font-semibold text-gray-700 mb-2">Abstract</h4>
              <p className="text-sm text-gray-700 leading-relaxed">{draft.abstract}</p>
            </div>
            <div className="p-4 bg-white rounded border border-gray-200">
              <h4 className="font-semibold text-gray-700 mb-2">Paper Outline</h4>
              <ol className="list-decimal list-inside space-y-2">
                {draft.outline?.map((section, idx) => (
                  <li key={idx} className="text-sm text-gray-700">{section}</li>
                ))}
              </ol>
            </div>
          </div>
        );

      case 'related_work':
        const relatedWork = data.related_work || data;
        return (
          <div className="space-y-4">
            <div className="p-4 bg-amber-50 rounded border border-amber-200">
              <h4 className="font-semibold text-amber-800 mb-2">
                Related Work Section ({relatedWork.word_count || 0} words, {relatedWork.papers_cited || 0} papers cited)
              </h4>
            </div>
            <div className="p-4 bg-white rounded border border-gray-200">
              <div className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                {relatedWork.section_text || 'No related work section generated'}
              </div>
            </div>
          </div>
        );

      case 'dataset':
        const datasetRec = data.dataset_recommendation || data;
        return (
          <div className="space-y-4">
            <div className="p-4 bg-teal-50 rounded border border-teal-200">
              <h4 className="font-semibold text-teal-800 text-lg">{datasetRec.primary_dataset}</h4>
              <p className="text-sm text-teal-600 mt-1">{datasetRec.size}</p>
            </div>
            <div className="p-4 bg-white rounded border border-gray-200">
              <p className="text-sm text-gray-700 mb-3"><strong>Description:</strong> {datasetRec.description}</p>
              <p className="text-sm text-gray-700 mb-3"><strong>Preprocessing:</strong> {datasetRec.preprocessing}</p>
              <p className="text-sm text-gray-700 mb-3"><strong>Why this fits:</strong> {datasetRec.suitability_rationale}</p>
              {datasetRec.url && (
                <a href={datasetRec.url} target="_blank" rel="noopener noreferrer" className="text-sm text-primary-600 hover:underline inline-flex items-center">
                  Download Dataset <ExternalLink className="w-3 h-3 ml-1" />
                </a>
              )}
            </div>
            {datasetRec.alternatives?.length > 0 && (
              <div className="p-3 bg-gray-50 rounded border border-gray-200">
                <h5 className="font-medium text-gray-700 text-sm mb-2">Alternative Datasets</h5>
                <div className="flex flex-wrap gap-2">
                  {datasetRec.alternatives.map((alt, idx) => (
                    <span key={idx} className="px-2 py-1 bg-white rounded text-xs text-gray-600 border border-gray-200">{alt}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        );

      case 'review':
        const review = data.review_feedback || data;
        const score = review.score || 5;
        const decision = review.estimated_decision || 'Unknown';
        const decisionColor = decision === 'Accept' ? 'bg-green-100 text-green-800' : 
                             decision === 'Minor Revision' ? 'bg-yellow-100 text-yellow-800' :
                             decision === 'Major Revision' ? 'bg-orange-100 text-orange-800' :
                             'bg-red-100 text-red-800';
        return (
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-gray-100 rounded border border-gray-200">
              <div>
                <h4 className="font-semibold text-gray-800">Peer Review Simulation</h4>
                <p className="text-sm text-gray-600">Score: {score}/10 | Confidence: {review.confidence}</p>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${decisionColor}`}>
                {decision}
              </span>
            </div>
            
            {review.strengths?.length > 0 && (
              <div className="p-4 bg-green-50 rounded border border-green-200">
                <h5 className="font-semibold text-green-800 text-sm mb-2">Strengths</h5>
                <ul className="space-y-1">
                  {review.strengths.map((s, idx) => (
                    <li key={idx} className="text-sm text-gray-700">• {s}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {review.weaknesses?.length > 0 && (
              <div className="p-4 bg-yellow-50 rounded border border-yellow-200">
                <h5 className="font-semibold text-yellow-800 text-sm mb-2">Weaknesses</h5>
                <ul className="space-y-1">
                  {review.weaknesses.map((w, idx) => (
                    <li key={idx} className="text-sm text-gray-700">• {w}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {review.critical_issues?.length > 0 && (
              <div className="p-4 bg-red-50 rounded border border-red-200">
                <h5 className="font-semibold text-red-800 text-sm mb-2">Critical Issues</h5>
                <ul className="space-y-1">
                  {review.critical_issues.map((ci, idx) => (
                    <li key={idx} className="text-sm text-gray-700">⚠️ {ci}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {review.suggestions_for_improvement?.length > 0 && (
              <div className="p-4 bg-blue-50 rounded border border-blue-200">
                <h5 className="font-semibold text-blue-800 text-sm mb-2">Suggestions for Improvement</h5>
                <ul className="space-y-1">
                  {review.suggestions_for_improvement.map((s, idx) => (
                    <li key={idx} className="text-sm text-gray-700">💡 {s}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {review.overall_assessment && (
              <div className="p-4 bg-white rounded border border-gray-200">
                <h5 className="font-semibold text-gray-700 text-sm mb-2">Overall Assessment</h5>
                <p className="text-sm text-gray-700">{review.overall_assessment}</p>
              </div>
            )}
          </div>
        );

      default:
        return <pre className="text-sm text-gray-700 overflow-x-auto">{JSON.stringify(data, null, 2)}</pre>;
    }
  };

  return (
    <div className={`rounded-lg border-2 ${config.borderColor} ${config.lightColor} overflow-hidden ${isActive ? 'ring-2 ring-offset-2 ring-primary-500' : ''}`}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={`w-full px-4 py-3 flex items-center justify-between ${config.color} text-white`}
      >
        <div className="flex items-center space-x-2">
          <Icon className="w-5 h-5" />
          <span className="font-semibold">{title}</span>
        </div>
        {isExpanded ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
      </button>
      {isExpanded && (
        <div className="p-4">
          {renderContent()}
        </div>
      )}
    </div>
  );
};

export default AgentOutputCard;
