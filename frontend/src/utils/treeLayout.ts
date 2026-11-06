import type { TreeNode } from '../types';

export interface LayoutNode {
  id: string;
  label: string;
  x: number;
  y: number;
  type: 'nonterminal' | 'terminal' | 'epsilon';
  production?: string;
}

export interface LayoutEdge {
  id: string;
  source: string;
  target: string;
}

export interface TreeLayout {
  nodes: LayoutNode[];
  edges: LayoutEdge[];
}

const HORIZONTAL_SPACING = 60;
const VERTICAL_SPACING = 90;
const NODE_WIDTH = 100;

function getSubtreeWidth(node: TreeNode): number {
  if (!node.children || node.children.length === 0) {
    return NODE_WIDTH + HORIZONTAL_SPACING;
  }
  const childWidths = node.children.map(getSubtreeWidth);
  return Math.max(childWidths.reduce((a, b) => a + b, 0), NODE_WIDTH + HORIZONTAL_SPACING);
}

function assignPositions(
  node: TreeNode,
  x: number,
  y: number,
  nodes: LayoutNode[],
  edges: LayoutEdge[]
): void {
  nodes.push({
    id: node.id,
    label: node.label,
    x,
    y,
    type: node.type,
    production: node.production,
  });

  if (!node.children || node.children.length === 0) return;

  const subtreeWidths = node.children.map(getSubtreeWidth);
  const totalWidth = subtreeWidths.reduce((a, b) => a + b, 0);

  let currentX = x - totalWidth / 2;

  node.children.forEach((child, idx) => {
    const childWidth = subtreeWidths[idx];
    const childX = currentX + childWidth / 2;
    const childY = y + VERTICAL_SPACING;

    edges.push({
      id: `${node.id}-${child.id}`,
      source: node.id,
      target: child.id,
    });

    assignPositions(child, childX, childY, nodes, edges);
    currentX += childWidth;
  });
}

export function computeTreeLayout(root: TreeNode): TreeLayout {
  const nodes: LayoutNode[] = [];
  const edges: LayoutEdge[] = [];

  const totalWidth = getSubtreeWidth(root);
  const startX = totalWidth / 2;

  assignPositions(root, startX, 40, nodes, edges);

  return { nodes, edges };
}
