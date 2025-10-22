import React from "react";
import { Routes, Route } from "react-router-dom";
import Landing from "./views/Landing";
import ModelRoute from "./ModelRoute";

export default function App() {
  console.log("API base:", import.meta.env.VITE_API_BASE);

  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/models/:modelId" element={<ModelRoute />} />
    </Routes>
  );
}
