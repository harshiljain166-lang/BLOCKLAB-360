export type NodeData={id:string;type:string;status:string;ip:string;height:number;peers:number;last_sync:string};
export type BlockData={index:number;timestamp:number;transactions:any[];previous_hash:string;nonce:number;hash:string;difficulty:number;miner_id:string};
export type Stats={total_nodes:number;active_nodes:number;idle_nodes:number;failed_nodes:number;total_transactions:number;pending_transactions:number;block_height:number;health:string;nodes:NodeData[];mining:any};
