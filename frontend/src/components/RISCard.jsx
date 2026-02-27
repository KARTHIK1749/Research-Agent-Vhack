import React from 'react';
import { BarChart3, Target, TrendingUp, AlertTriangle, Brain, Sparkles } from 'lucide-react';

const RISCard = ({ researchScores, refinedOutput, clusterAnalysis }) => {
  if (!researchScores && !refinedOutput && !clusterAnalysis) {
    return null;
  }

  const getScoreColor = (score, max = 10) => {
    const percentage = (score / max) * 100;
    if (percentage >= 80) return 'text-green-600 bg-green-50 border-green-200';
    if (percentage >= 60) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  const getScoreWidth = (score, max = 10) => {
    return `${(score / max) * 100}%`;
  };

  return (
    <div className="space-y-6">
      {/* Research Intelligence Score */}
      {researchScores && (
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 p-4">
            <div className="flex items-center text-white">
              <Target className="w-6 h-6 mr-2" />
              <h3 className="text-lg font-semibold">Research Intelligence Score (RIS)</h3>
            </div>
          </div>
          
          <div className="p-6">
            {/* Overall RIS Score */}
            <div className="mb-6 text-center">
              <div className="text-4xl font-bold text-purple-600 mb-2">
                {researchScores.ris?.toFixed(1) || 'N/A'}
                <span className="text-lg text-gray-500">/10</span>
              </div>
              <p className="text-sm text-gray-600">Overall Research Intelligence Score</p>
            </div>

            {/* Individual Scores */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className={`p-4 rounded-lg border ${getScoreColor(researchScores.novelty)}`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">Novelty</span>
                  <span className="font-bold">{researchScores.novelty?.toFixed(1) || 'N/A'}/10</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-current h-2 rounded-full transition-all duration-500"
                    style={{ width: getScoreWidth(researchScores.novelty || 0) }}
                  />
                </div>
                <p className="text-xs mt-2 opacity-75">Distance from cluster centroids</p>
              </div>

              <div className={`p-4 rounded-lg border ${getScoreColor(researchScores.feasibility)}`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">Feasibility</span>
                  <span className="font-bold">{researchScores.feasibility?.toFixed(1) || 'N/A'}/10</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-current h-2 rounded-full transition-all duration-500"
                    style={{ width: getScoreWidth(researchScores.feasibility || 0) }}
                  />
                </div>
                <p className="text-xs mt-2 opacity-75">Technical complexity assessment</p>
              </div>

              <div className={`p-4 rounded-lg border ${getScoreColor(researchScores.impact)}`}>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium">Impact</span>
                  <span className="font-bold">{researchScores.impact?.toFixed(1) || 'N/A'}/10</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-current h-2 rounded-full transition-all duration-500"
                    style={{ width: getScoreWidth(researchScores.impact || 0) }}
                  />
                </div>
                <p className="text-xs mt-2 opacity-75">Potential contribution</p>
              </div>

              <div className={`p-4 rounded-lg border ${getScoreColor(10 - (researchScores.risk || 0))}`}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center">
                    <AlertTriangle className="w-4 h-4 mr-1" />
                    <span className="font-medium">Risk</span>
                  </div>
                  <span className="font-bold">{researchScores.risk?.toFixed(1) || 'N/A'}/10</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-current h-2 rounded-full transition-all duration-500"
                    style={{ width: getScoreWidth(researchScores.risk || 0) }}
                  />
                </div>
                <p className="text-xs mt-2 opacity-75">Failure probability (lower is better)</p>
              </div>
            </div>

            <div className="mt-4 p-3 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-600 text-center">
                <strong>RIS Formula:</strong> 0.4 × Novelty + 0.3 × Feasibility + 0.3 × Impact
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Cluster Analysis */}
      {clusterAnalysis && (
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
          <div className="bg-gradient-to-r from-blue-600 to-cyan-600 p-4">
            <div className="flex items-center text-white">
              <BarChart3 className="w-6 h-6 mr-2" />
              <h3 className="text-lg font-semibold">Analytical Gap Engine</h3>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Cluster Density</h4>
                <div className="space-y-2">
                  {Object.entries(clusterAnalysis.density || {}).map(([clusterId, count]) => (
                    <div key={clusterId} className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Cluster {clusterId}</span>
                      <div className="flex items-center">
                        <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${((count || 0) / Math.max(...Object.values(clusterAnalysis.density || {}))) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium w-8">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Gap Analysis</h4>
                <div className="space-y-3">
                  <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-center text-red-800">
                      <Target className="w-4 h-4 mr-2" />
                      <span className="font-medium">Sparsest Cluster</span>
                    </div>
                    <p className="text-sm text-red-700 mt-1">
                      Cluster {clusterAnalysis.sparsest_cluster} - Most underexplored research area
                    </p>
                  </div>
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center text-blue-800">
                      <BarChart3 className="w-4 h-4 mr-2" />
                      <span className="font-medium">Total Papers</span>
                    </div>
                    <p className="text-sm text-blue-700 mt-1">
                      {clusterAnalysis.total_papers} papers analyzed across {clusterAnalysis.n_clusters} clusters
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Reflection Results */}
      {refinedOutput && (
        <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
          <div className="bg-gradient-to-r from-amber-600 to-orange-600 p-4">
            <div className="flex items-center text-white">
              <Brain className="w-6 h-6 mr-2" />
              <h3 className="text-lg font-semibold">Self-Reflection Results</h3>
            </div>
          </div>
          
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Identified Issues</h4>
                <div className="space-y-2">
                  {refinedOutput.criticisms?.map((criticism, index) => (
                    <div key={index} className="flex items-start p-3 bg-amber-50 border border-amber-200 rounded-lg">
                      <AlertTriangle className="w-4 h-4 text-amber-600 mr-2 mt-0.5 flex-shrink-0" />
                      <span className="text-sm text-gray-700">{criticism}</span>
                    </div>
                  )) || <p className="text-sm text-gray-500">No criticisms identified</p>}
                </div>
              </div>

              <div>
                <h4 className="font-semibold text-gray-900 mb-3">Improvement Metrics</h4>
                <div className="space-y-3">
                  <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-green-800">RIS Improvement</span>
                      <span className={`font-bold ${
                        (refinedOutput.improvement?.ris_change || 0) > 0 ? 'text-green-600' : 'text-gray-600'
                      }`}>
                        {(refinedOutput.improvement?.ris_change || 0) > 0 ? '+' : ''}{refinedOutput.improvement?.ris_change?.toFixed(1) || '0.0'}
                      </span>
                    </div>
                  </div>
                  <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-blue-800">Confidence</span>
                      <span className="font-bold text-blue-600">
                        {((refinedOutput.confidence || 0) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>

                {refinedOutput.refined_hypothesis && (
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                    <h5 className="font-medium text-gray-900 mb-2 flex items-center">
                      <Sparkles className="w-4 h-4 mr-2 text-amber-600" />
                      Refined Hypothesis
                    </h5>
                    <p className="text-sm text-gray-700 italic">
                      "{refinedOutput.refined_hypothesis}"
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RISCard;
