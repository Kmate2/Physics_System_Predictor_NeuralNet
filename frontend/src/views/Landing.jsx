import React from "react";
import Tiles from "../components/Tiles";

export default function Landing() {
  return (
    <div className="container centerWrap">
      <h1 className="title">WELCOME TO THE PHYSICS SYSTEM SIMULATOR APP</h1>
      <div className="subtitle">
        PICK A MODEL AND SIMULATE THE CURVE OF THE MOVEMENT!
      </div>
      <Tiles />
    </div>
  );
}
