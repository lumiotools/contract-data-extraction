import React from "react";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Loader2 } from "lucide-react";

export function LoadingAnimation() {
  const [progress, setProgress] = React.useState(0);
  const [timeElapsed, setTimeElapsed] = React.useState(0);
  const [currentPhrase, setCurrentPhrase] = React.useState(0);

  const analysisPhrases = [
    "Analyzing contract terms...",
    "Calculating potential savings...",
    "Comparing market rates...",
    "Identifying optimization opportunities...",
    "Generating discount recommendations...",
  ];

  React.useEffect(() => {
    const progressTimer = setInterval(() => {
      setProgress((oldProgress) => {
        const newProgress = oldProgress + 5;
        return newProgress >= 100 ? 100 : newProgress;
      });
    }, 20 * 1000);

    const timeTimer = setInterval(() => {
      setTimeElapsed((prevTime) => prevTime + 1);
    }, 1000);

    const phraseTimer = setInterval(() => {
      setCurrentPhrase((prev) => (prev + 1) % analysisPhrases.length);
    }, 4000);

    return () => {
      clearInterval(progressTimer);
      clearInterval(timeTimer);
      clearInterval(phraseTimer);
    };
  }, []);

  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-[#1C1C28]/80 backdrop-blur-md" />
      <div className="relative h-full flex items-center justify-center">
        <Card className="w-full max-w-md mx-auto bg-[#23232F]/90 border-[#2A2A36]">
          <div className="p-8 flex flex-col items-center space-y-6">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-tr from-purple-500/30 to-orange-500/30 blur-xl rounded-full" />
              <Loader2 className="w-16 h-16 text-orange-500 animate-spin relative z-10" />
            </div>

            <div className="text-center space-y-2">
              <h2 className="text-2xl font-bold text-white">
                Analyzing Your Contract
              </h2>
              <p className="text-sm text-gray-400">
                This may take up to 200 seconds
              </p>
            </div>

            <div className="w-full space-y-2">
              <Progress value={progress} className="h-2 bg-[#2A2A36]" />
              <div className="flex justify-between text-sm">
                <p className="text-gray-400">{progress}% Complete</p>
                <div className="text-orange-500 font-bold bg-orange-500/10 px-3 py-1 rounded-full animate-pulse">
                  <span>{timeElapsed}s elapsed</span>
                </div>
              </div>
            </div>

            <div className="text-center space-y-2">
              <p className="text-gray-400 min-h-[24px] transition-all duration-300">
                {analysisPhrases[currentPhrase]}
              </p>
              <div className="flex items-center justify-center space-x-1">
                <div
                  className="w-1 h-1 rounded-full bg-orange-500 animate-bounce"
                  style={{ animationDelay: "0ms" }}
                />
                <div
                  className="w-1 h-1 rounded-full bg-orange-500 animate-bounce"
                  style={{ animationDelay: "150ms" }}
                />
                <div
                  className="w-1 h-1 rounded-full bg-orange-500 animate-bounce"
                  style={{ animationDelay: "300ms" }}
                />
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
