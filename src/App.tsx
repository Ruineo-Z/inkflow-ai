import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "@/pages/Home";
import Story from "@/pages/Story";
import Stories from "@/pages/Stories";
import ApiDocs from "@/pages/ApiDocs";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import UserCenter from "@/pages/UserCenter";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/story/:storyId" element={<Story />} />
        <Route path="/stories" element={<Stories />} />
        <Route path="/api-docs" element={<ApiDocs />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/user-center" element={<UserCenter />} />
      </Routes>
    </Router>
  );
}
