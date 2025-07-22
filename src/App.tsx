import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "@/pages/Home";
import Story from "@/pages/Story";
import Stories from "@/pages/Stories";
import ApiDocs from "@/pages/ApiDocs";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/story/:storyId" element={<Story />} />
        <Route path="/stories" element={<Stories />} />
        <Route path="/api-docs" element={<ApiDocs />} />
      </Routes>
    </Router>
  );
}
