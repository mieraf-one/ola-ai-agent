"use client";

import React, { useState } from "react";

interface ApprovalCardProps {
  plan: string[];
  onApprove: () => void;
  onUpdatePlan: (newPlan: string[]) => void;
  onReject: () => void;
  disabled?: boolean;
}

export default function ApprovalCard({
  plan,
  onApprove,
  onUpdatePlan,
  onReject,
  disabled = false,
}: ApprovalCardProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedPlanText, setEditedPlanText] = useState(plan.join("\n"));
  const [actionTaken, setActionTaken] = useState<"approved" | "updated" | "rejected" | null>(null);

  const handleApprove = () => {
    setActionTaken("approved");
    onApprove();
  };

  const handleSaveAndRun = () => {
    const newSteps = editedPlanText
      .split("\n")
      .map((line) => line.replace(/^\d+[\.\-\)]\s*/, "").trim())
      .filter((line) => line.length > 0);

    setActionTaken("updated");
    setIsEditing(false);
    onUpdatePlan(newSteps.length > 0 ? newSteps : plan);
  };

  const handleReject = () => {
    setActionTaken("rejected");
    onReject();
  };

  if (actionTaken === "approved" || actionTaken === "updated") {
    return (
      <div className="my-2 p-2.5 bg-surface-container-low border border-primary/30 rounded-lg text-xs flex items-center gap-2 text-on-surface shadow-2xs">
        <span className="material-symbols-outlined text-primary text-[17px]">check_circle</span>
        <span className="font-medium">
          Plan {actionTaken === "updated" ? "modified and approved" : "approved"}. Resuming code generation...
        </span>
      </div>
    );
  }

  if (actionTaken === "rejected") {
    return (
      <div className="my-2 p-2.5 bg-error-container/40 border border-error/30 rounded-lg text-xs flex items-center gap-2 text-on-error-container shadow-2xs">
        <span className="material-symbols-outlined text-error text-[17px]">cancel</span>
        <span className="font-medium">Plan rejected by user. Task was cancelled.</span>
      </div>
    );
  }

  return (
    <div className="my-2 p-3 bg-surface-container-low border border-primary/25 rounded-xl shadow-2xs text-xs animate-in fade-in duration-300">
      <div className="flex items-center justify-between mb-1.5 pb-1 border-b border-outline-variant/40">
        <div className="flex items-center gap-1.5 text-primary font-semibold">
          <span className="material-symbols-outlined text-primary text-[17px]">supervisor_account</span>
          <span className="font-semibold text-xs sm:text-[13px]">Plan Review &amp; Approval (Human-in-the-Loop)</span>
        </div>
        <span className="font-label-badge text-[9px] text-primary bg-primary-fixed px-2 py-0.2 rounded-full font-bold">
          Paused Before Code Generation
        </span>
      </div>

      <p className="text-on-surface-variant text-xs mb-2 leading-relaxed">
        LangGraph paused execution so you can review and approve the implementation roadmap before any files are generated:
      </p>

      {/* Plan Display / Editor */}
      {isEditing ? (
        <div className="mb-2 space-y-1.5">
          <textarea
            value={editedPlanText}
            onChange={(e) => setEditedPlanText(e.target.value)}
            disabled={disabled}
            rows={4}
            className="w-full p-2 bg-surface-container-lowest border border-primary rounded-lg text-on-surface font-label-code text-xs focus:outline-none focus:ring-1 focus:ring-primary/30 leading-relaxed resize-y shadow-inner"
            placeholder="One plan step per line..."
          />
          <div className="flex justify-end gap-1">
            <button
              onClick={() => setIsEditing(false)}
              className="px-3 py-1 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface text-xs transition"
            >
              Cancel
            </button>
            <button
              onClick={handleSaveAndRun}
              className="px-3 py-1 rounded-full bg-primary hover:bg-primary-container text-on-primary text-xs font-semibold flex items-center gap-1 transition shadow-2xs"
            >
              <span className="material-symbols-outlined text-[14px]">play_arrow</span>
              Save &amp; Proceed
            </button>
          </div>
        </div>
      ) : (
        <ol className="list-decimal list-inside space-y-1 p-2.5 bg-surface-container-lowest rounded-lg border border-outline-variant/60 text-on-surface mb-2 text-xs leading-relaxed shadow-2xs">
          {plan.map((step, idx) => (
            <li key={idx} className="pl-0.5">
              <span className="text-on-surface font-medium">{step}</span>
            </li>
          ))}
        </ol>
      )}

      {/* Action Buttons */}
      {!isEditing && (
        <div className="flex flex-wrap items-center gap-1.5 pt-0.5">
          <button
            onClick={handleApprove}
            disabled={disabled}
            className="flex-1 min-w-[150px] flex items-center justify-center gap-1 py-1.5 px-3 rounded-full bg-primary hover:bg-primary-container text-on-primary text-xs font-semibold transition disabled:opacity-50 shadow-2xs"
          >
            <span className="material-symbols-outlined text-[15px]">check</span>
            Approve &amp; Generate Code
          </button>

          <button
            onClick={() => setIsEditing(true)}
            disabled={disabled}
            className="flex items-center gap-1 py-1.5 px-3 rounded-full bg-surface-container hover:bg-surface-container-high text-on-surface text-xs font-medium border border-outline-variant/60 transition disabled:opacity-50"
          >
            <span className="material-symbols-outlined text-primary text-[14px]">edit</span>
            Edit Plan
          </button>

          <button
            onClick={handleReject}
            disabled={disabled}
            className="flex items-center gap-1 py-1.5 px-3 rounded-full bg-error-container/60 hover:bg-error-container text-on-error-container text-xs font-medium transition disabled:opacity-50"
          >
            <span className="material-symbols-outlined text-error text-[14px]">close</span>
            Reject
          </button>
        </div>
      )}
    </div>
  );
}
