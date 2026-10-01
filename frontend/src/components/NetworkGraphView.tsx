import { useState } from "react"
import type { NetworkNode, NetworkEdge } from "../types/listing"
import RiskBadge from "./RiskBadge"
import { networkGroupInfo } from "../data/mockData"
import { Users, Globe, MessageCircle, AlertTriangle, Download, ZoomIn, ZoomOut } from "lucide-react"

interface NetworkGraphViewProps {
  nodes: NetworkNode[]
  edges: NetworkEdge[]
}

const riskColors: Record<string, string> = {
  high: "#dc2626",
  medium: "#f97316",
  low: "#16a34a",
}

const connectionFilters = [
  { id: "all", label: "All Connections" },
  { id: "phone", label: "Shared Phone Numbers" },
  { id: "text", label: "Identical Text" },
  { id: "payment", label: "Shared Payment Account" },
]

export default function NetworkGraphView({ nodes, edges }: NetworkGraphViewProps) {
  const [selectedNode, setSelectedNode] = useState<string | null>(nodes[0]?.id ?? null)
  const [connectionFilter, setConnectionFilter] = useState("all")
  const [zoom, setZoom] = useState(1)

  const findNode = (id: string) => nodes.find((n) => n.id === id)

  const visibleEdges = edges.filter((e) => {
    if (connectionFilter === "all") return true
    if (connectionFilter === "phone") return e.connectionType === "phone" || e.connectionType === "whatsapp"
    return e.connectionType === connectionFilter
  })

  const connectedEdges = visibleEdges.filter(
    (e) => e.source === selectedNode || e.target === selectedNode
  )
  const connectedNodeIds = new Set(connectedEdges.flatMap((e) => [e.source, e.target]))

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap gap-2">
          {connectionFilters.map((f) => (
            <button
              key={f.id}
              onClick={() => setConnectionFilter(f.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                connectionFilter === f.id
                  ? "bg-emerald-600 text-white"
                  : "bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setZoom((z) => Math.max(0.6, z - 0.2))}
            className="p-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <ZoomOut size={16} />
          </button>
          <button
            onClick={() => setZoom((z) => Math.min(1.8, z + 0.2))}
            className="p-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <ZoomIn size={16} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100">Interactive Syndicate Canvas</h2>
            <span className="text-xs bg-emerald-50 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400 px-2 py-0.5 rounded-full font-medium">
              1 Cluster Visible
            </span>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Click a job listing to see how it's connected to others.
          </p>

          <div
            className="relative w-full h-[420px] bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-100 dark:border-gray-700 overflow-hidden"
            style={{ transform: `scale(${zoom})`, transformOrigin: "center" }}
          >
            <svg className="absolute inset-0 w-full h-full">
              {visibleEdges.map((edge, i) => {
                const source = findNode(edge.source)
                const target = findNode(edge.target)
                if (!source || !target) return null
                const isHighlighted = edge.source === selectedNode || edge.target === selectedNode
                return (
                  <line
                    key={i}
                    x1={`${source.x}%`}
                    y1={`${source.y}%`}
                    x2={`${target.x}%`}
                    y2={`${target.y}%`}
                    stroke={isHighlighted ? "#059669" : "#d1d5db"}
                    strokeWidth={isHighlighted ? 2 : 1}
                  />
                )
              })}
            </svg>

            {visibleEdges.map((edge, i) => {
              const source = findNode(edge.source)
              const target = findNode(edge.target)
              if (!source || !target) return null
              const midX = (source.x + target.x) / 2
              const midY = (source.y + target.y) / 2
              return (
                <div
                  key={`label-${i}`}
                  className="absolute -translate-x-1/2 -translate-y-1/2 bg-white dark:bg-gray-800 border border-emerald-200 dark:border-emerald-700 text-emerald-700 dark:text-emerald-400 text-[10px] font-medium px-2 py-0.5 rounded-full shadow-sm whitespace-nowrap"
                  style={{ left: `${midX}%`, top: `${midY}%` }}
                >
                  {edge.label}
                </div>
              )
            })}

            {nodes.map((node) => (
              <button
                key={node.id}
                onClick={() => setSelectedNode(node.id)}
                className="absolute -translate-x-1/2 -translate-y-1/2 flex flex-col items-center group"
                style={{ left: `${node.x}%`, top: `${node.y}%` }}
              >
                <div
                  className={`w-5 h-5 rounded-full border-2 transition-all ${
                    selectedNode === node.id
                      ? "scale-125 border-emerald-600"
                      : connectedNodeIds.has(node.id)
                      ? "border-emerald-400"
                      : "border-white dark:border-gray-800"
                  }`}
                  style={{ backgroundColor: riskColors[node.riskLevel] }}
                />
                <span className="mt-1 text-xs font-medium text-gray-700 dark:text-gray-200 bg-white dark:bg-gray-800 px-2 py-0.5 rounded shadow-sm whitespace-nowrap">
                  {node.jobTitle}
                </span>
              </button>
            ))}
          </div>

          <div className="flex gap-4 mt-4 text-xs text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-red-600 inline-block" /> High Risk
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-orange-500 inline-block" /> Medium Risk
            </span>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase">Investigative Dossier</p>
              <h2 className="text-lg font-bold text-gray-900 dark:text-gray-100 mt-1">
                Selected Scam Network: {networkGroupInfo.groupId}
              </h2>
            </div>
            <span className="text-xs bg-red-50 dark:bg-red-950 text-red-600 dark:text-red-400 px-2 py-1 rounded-full font-medium whitespace-nowrap">
              {networkGroupInfo.status}
            </span>
          </div>

          <div className="mt-4 p-3 bg-emerald-50 dark:bg-emerald-950 rounded-lg text-sm text-emerald-900 dark:text-emerald-200">
            <strong>In Simple Terms:</strong> {networkGroupInfo.simpleExplanation}
          </div>

          <div className="mt-4 space-y-3">
            <p className="text-xs font-semibold text-gray-400 uppercase">Network Breakdown</p>

            <div className="flex items-start gap-2 text-sm">
              <Users size={16} className="text-gray-400 mt-0.5" />
              <span className="font-medium text-gray-800 dark:text-gray-200">
                {networkGroupInfo.totalConnectedAds} Fake Job Ads connected together
              </span>
            </div>

            <div className="flex items-start gap-2 text-sm">
              <Globe size={16} className="text-gray-400 mt-0.5" />
              <span className="text-gray-800 dark:text-gray-200">
                <span className="font-medium">{networkGroupInfo.countriesTargeted.length} Countries targeted:</span>{" "}
                {networkGroupInfo.countriesTargeted.map((c) => `${c.name} (${c.count})`).join(", ")}
              </span>
            </div>

            <div className="flex items-start gap-2 text-sm">
              <MessageCircle size={16} className="text-gray-400 mt-0.5" />
              <span className="text-gray-800 dark:text-gray-200">
                <span className="font-medium">Shared WhatsApp:</span> {networkGroupInfo.sharedWhatsApp}
              </span>
            </div>

            <div className="flex items-start gap-2 text-sm">
              <AlertTriangle size={16} className="text-gray-400 mt-0.5" />
              <span className="text-gray-800 dark:text-gray-200">
                <span className="font-medium">Common Scam Trick:</span> {networkGroupInfo.commonScamTrick}
              </span>
            </div>
          </div>

          <div className="mt-4">
            <p className="text-xs font-semibold text-gray-400 uppercase mb-2">Connected Ads in This Group</p>
            <div className="space-y-2">
              {nodes.map((node) => (
                <div
                  key={node.id}
                  className="flex items-center justify-between text-sm border border-gray-100 dark:border-gray-700 rounded-lg p-2"
                >
                  <div>
                    <p className="font-medium text-gray-800 dark:text-gray-200">{node.jobTitle}</p>
                    <p className="text-xs text-gray-400">{node.entity}</p>
                  </div>
                  <RiskBadge level={node.riskLevel} />
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={() =>
              alert(
                `Network report submitted for review.\n\nThis will notify job platforms about ${networkGroupInfo.totalConnectedAds} connected fake listings linked to ${networkGroupInfo.groupId}.`
              )
            }
            className="w-full mt-4 px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700 transition-colors"
          >
             Report Network to Job Platforms
          </button>

          <button
            onClick={() => alert("PDF export coming soon.")}
            className="w-full mt-2 flex items-center justify-center gap-2 px-4 py-2 border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <Download size={16} />
            Download Evidence Summary (PDF)
          </button>
        </div>
      </div>
    </div>
  )
}