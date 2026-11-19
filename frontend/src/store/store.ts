import {create} from 'zustand';
type State={page:string;view:'3d'|'2d'|'ledger';selectedNode:string|null;setPage:(p:string)=>void;setView:(v:'3d'|'2d'|'ledger')=>void;selectNode:(id:string|null)=>void};
export const useStore=create<State>(set=>({page:'Overview',view:'3d',selectedNode:'miner-01',setPage:page=>set({page}),setView:view=>set({view}),selectNode:selectedNode=>set({selectedNode})}));
