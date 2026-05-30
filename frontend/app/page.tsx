'use client';

import Link from 'next/link';
import { ArrowRight, FileText, MessageSquare, Search, Zap } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Zap className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold">Atlas</span>
          </div>
          <nav className="flex items-center space-x-4">
            <Link
              href="/auth/login"
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              Login
            </Link>
            <Link
              href="/auth/signup"
              className="bg-primary text-primary-foreground px-4 py-2 rounded-md hover:bg-primary/90 transition-colors"
            >
              Get Started
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1">
        <section className="container mx-auto px-4 py-24 text-center">
          <h1 className="text-5xl font-bold tracking-tight mb-6">
            Your Codebase,{' '}
            <span className="text-primary">Understood</span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
            Upload your repositories, documentation, and engineering knowledge.
            Ask questions and get answers with citations.
          </p>
          <div className="flex items-center justify-center space-x-4">
            <Link
              href="/auth/signup"
              className="bg-primary text-primary-foreground px-6 py-3 rounded-md hover:bg-primary/90 transition-colors flex items-center space-x-2"
            >
              <span>Start for Free</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="#features"
              className="border border-input px-6 py-3 rounded-md hover:bg-accent transition-colors"
            >
              Learn More
            </Link>
          </div>
        </section>

        {/* Features Section */}
        <section id="features" className="container mx-auto px-4 py-24">
          <h2 className="text-3xl font-bold text-center mb-12">
            Built for Engineering Teams
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <FeatureCard
              icon={<FileText className="h-10 w-10" />}
              title="Document Upload"
              description="Upload PDFs, markdown, code files, and more. We parse and index everything automatically."
            />
            <FeatureCard
              icon={<Search className="h-10 w-10" />}
              title="Intelligent Search"
              description="Hybrid search combining semantic understanding with keyword matching for precise results."
            />
            <FeatureCard
              icon={<MessageSquare className="h-10 w-10" />}
              title="Conversational AI"
              description="Ask questions in natural language and get answers with citations to your source documents."
            />
          </div>
        </section>

        {/* Example Queries Section */}
        <section className="bg-muted py-24">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-12">
              Questions You Can Ask
            </h2>
            <div className="grid md:grid-cols-2 gap-4 max-w-3xl mx-auto">
              <QueryExample query="How does authentication work in this codebase?" />
              <QueryExample query="Which services interact with Redis?" />
              <QueryExample query="Explain the payment flow architecture" />
              <QueryExample query="What APIs are involved in user registration?" />
              <QueryExample query="Show me files related to rate limiting" />
              <QueryExample query="Generate onboarding docs for new developers" />
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-muted-foreground">
          <p>Atlas - AI Codebase Knowledge Assistant</p>
          <p className="text-sm mt-2">Built with FastAPI, Next.js, LangGraph, and Qdrant</p>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-card border rounded-lg p-6">
      <div className="text-primary mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-muted-foreground">{description}</p>
    </div>
  );
}

function QueryExample({ query }: { query: string }) {
  return (
    <div className="bg-card border rounded-lg p-4 flex items-center space-x-3">
      <MessageSquare className="h-5 w-5 text-muted-foreground flex-shrink-0" />
      <span className="text-sm">{query}</span>
    </div>
  );
}
