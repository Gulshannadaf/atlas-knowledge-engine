'use client';

import { useState, useEffect } from 'react';
import { BarChart3, Play, Loader2, CheckCircle, XCircle, Clock } from 'lucide-react';

interface Evaluation {
  id: string;
  name: string;
  description: string | null;
  status: 'pending' | 'running' | 'completed' | 'failed';
  metrics: {
    context_precision?: number;
    context_recall?: number;
    faithfulness?: number;
    answer_relevancy?: number;
    total_queries?: number;
    average_latency_ms?: number;
    average_cost_usd?: number;
  };
  created_at: string;
  completed_at: string | null;
}

export default function EvaluationPage() {
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  const fetchEvaluations = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/evaluation`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (response.ok) {
        const data = await response.json();
        setEvaluations(data.evaluations);
      }
    } catch (error) {
      console.error('Error fetching evaluations:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvaluations();
  }, []);

  const handleRunEvaluation = async () => {
    setCreating(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/evaluation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          name: `Evaluation ${new Date().toLocaleString()}`,
          description: 'Manual evaluation run',
        }),
      });

      if (response.ok) {
        await fetchEvaluations();
      }
    } catch (error) {
      console.error('Error creating evaluation:', error);
    } finally {
      setCreating(false);
    }
  };

  const getStatusIcon = (status: Evaluation['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-destructive" />;
      case 'running':
        return <Loader2 className="h-5 w-5 animate-spin text-blue-500" />;
      default:
        return <Clock className="h-5 w-5 text-muted-foreground" />;
    }
  };

  const formatMetric = (value: number | undefined) => {
    if (value === undefined) return '-';
    return (value * 100).toFixed(1) + '%';
  };

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Evaluation</h1>
          <p className="text-muted-foreground">
            Run RAG quality evaluations using RAGAS metrics
          </p>
        </div>
        <button
          onClick={handleRunEvaluation}
          disabled={creating}
          className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
        >
          {creating ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Play className="h-4 w-4" />
          )}
          <span>Run Evaluation</span>
        </button>
      </div>

      {/* Latest metrics */}
      {evaluations.length > 0 && evaluations[0].status === 'completed' && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <MetricCard
            label="Context Precision"
            value={formatMetric(evaluations[0].metrics.context_precision)}
          />
          <MetricCard
            label="Context Recall"
            value={formatMetric(evaluations[0].metrics.context_recall)}
          />
          <MetricCard
            label="Faithfulness"
            value={formatMetric(evaluations[0].metrics.faithfulness)}
          />
          <MetricCard
            label="Answer Relevancy"
            value={formatMetric(evaluations[0].metrics.answer_relevancy)}
          />
        </div>
      )}

      {/* Evaluations list */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Evaluation History</h2>

        {loading ? (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-6 w-6 animate-spin" />
          </div>
        ) : evaluations.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No evaluations run yet</p>
            <p className="text-sm mt-1">
              Click "Run Evaluation" to measure RAG quality
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {evaluations.map((evaluation) => (
              <div
                key={evaluation.id}
                className="flex items-center justify-between p-4 bg-card border rounded-lg"
              >
                <div className="flex items-center space-x-4">
                  {getStatusIcon(evaluation.status)}
                  <div>
                    <p className="font-medium">{evaluation.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(evaluation.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                {evaluation.status === 'completed' && evaluation.metrics && (
                  <div className="flex items-center space-x-4 text-sm">
                    <span>
                      Faithfulness: {formatMetric(evaluation.metrics.faithfulness)}
                    </span>
                    <span>
                      Queries: {evaluation.metrics.total_queries || 0}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-card border rounded-lg p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
    </div>
  );
}
