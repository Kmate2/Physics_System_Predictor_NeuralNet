import { useParams, useNavigate, Navigate } from "react-router-dom";
import { models } from "./models";
import ModelRunner from "./views/ModelRunner";

export default function ModelRoute() {
  const { modelId } = useParams();
  const cfg = models[modelId];
  const navigate = useNavigate();
  if (!cfg) return <Navigate to="/" replace />;
  return <ModelRunner config={cfg} onBack={() => navigate(-1)} />;
}
