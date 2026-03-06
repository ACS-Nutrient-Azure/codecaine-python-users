import { createBrowserRouter } from "react-router";
import { Layout } from "./components/Layout";
import { Home } from "./pages/Home";
import { RecordHistory } from "./pages/RecordHistory";
import { Recommendation } from "./pages/Recommendation";
import { RecommendationResult } from "./pages/RecommendationResult";
import { Chatbot } from "./pages/Chatbot";
import { MyPage } from "./pages/MyPage";
import { AnalysisHistory } from "./pages/AnalysisHistory";
import { Settings } from "./pages/Settings";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: Home },
      { path: "record", Component: RecordHistory },
      { path: "recommendation", Component: Recommendation },
      { path: "recommendation-result", Component: RecommendationResult },
      { path: "chatbot", Component: Chatbot },
      { path: "my-page", Component: MyPage },
      { path: "analysis-history", Component: AnalysisHistory },
      { path: "settings", Component: Settings },
    ],
  },
]);