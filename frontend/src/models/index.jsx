import FormProjectile from "../components/FormProjectile";
import TrajectoryPlot from "../components/TrajectoryPlot";
import { physicsFrom as projectilePhysics } from "../utils/physics";

import StatBlock from "../components/StatBlock";

export const models = {
  projectile: {
    id: "projectile",
    order: 1,
    title: "Ideal Projectile (No Drag)",
    tileSubtitle:
      "Inputs: velocity (m/s), angle (deg).\nModel a simple ideal projectile throw curve!",

    Form: FormProjectile,
    Plot: TrajectoryPlot,
    computePhysics: ({ velocity, angle }) => projectilePhysics(velocity, angle),

    buildRequest: ({ velocity, angle }) => ({
      path: "/predict",
      body: { velocity, angle_deg: angle },
    }),
    mapResponse: (data) => {
      const pr = data?.prediction;
      if (!pr) throw new Error("Empty prediction");
      return { R: pr.range_m, H: pr.max_height_m, T: pr.flight_time_s };
    },
    renderStats: ({ phys, ai }) => (
      <div className="statsRow">
        <StatBlock title="Physics" R={phys.R} H={phys.H} T={phys.T} />
        <StatBlock title="AI" R={ai.R} H={ai.H} T={ai.T} />
      </div>
    ),
  },

  pendulum: {
    id: "pendulum",
    order: 2,
    title: "Simple Pendulum",
    enabled: false,
  },

  EXTRAKAOTIKUSRENDSZER: {
    id: "EXTRAKAOTIKUSRENDSZER",
    order: 3,
    title: "EXTRAKAOTIKUSRENDSZER",
    enabled: false,
  },
};
