interface Peer {
  id: string;
  username: string;
  permission: string;
}

interface Props {
  peers: Peer[];
  currentUserId: string;
}

const COLORS = ["#1a73e8", "#188038", "#c2185b", "#f57c00", "#7b1fa2"];

export default function PresenceBar({ peers, currentUserId }: Props) {
  const others = peers.filter((p) => p.id !== currentUserId);
  if (others.length === 0) return null;

  return (
    <div className="presence-bar">
      {others.map((peer, i) => (
        <div
          key={peer.id}
          className="presence-avatar"
          title={`${peer.username} (${peer.permission})`}
          style={{ background: COLORS[i % COLORS.length] }}
        >
          {peer.username[0].toUpperCase()}
        </div>
      ))}
      <span className="presence-label">
        {others.length === 1 ? `${others[0].username} is here` : `${others.length} others here`}
      </span>
    </div>
  );
}
