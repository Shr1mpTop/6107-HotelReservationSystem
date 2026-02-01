"use client";

import "./Loading.css";

interface LoadingProps {
  text?: string;
  subtext?: string;
}

export default function Loading({
  text = "Loading...",
  subtext = "Please wait",
}: LoadingProps) {
  return (
    <div className="loading-overlay">
      <div className="loading-content">
        <div className="loading-spinner">
          <div className="spinner-ring"></div>
          <div className="spinner-ring"></div>
          <div className="spinner-ring"></div>
        </div>
        <div className="loading-text">{text}</div>
        <div className="loading-subtext">{subtext}</div>
      </div>
    </div>
  );
}

export function InlineLoader() {
  return <div className="inline-loader"></div>;
}
