import { createBrowserRouter } from "react-router-dom";

import { AdminDebugPage } from "../features/admin-debug/AdminDebugPage";
import { CostsPage } from "../features/costs/CostsPage";
import { DataQualityPage } from "../features/data-quality/DataQualityPage";
import { DevicesPage } from "../features/devices/DevicesPage";
import { OperationsWindowPage } from "../features/operations-window/OperationsWindowPage";
import { OverviewPage } from "../features/overview/OverviewPage";
import { TasksPage } from "../features/tasks/TasksPage";
import { TriagePage } from "../features/triage/TriagePage";
import { WorkReportsPage } from "../features/work-reports/WorkReportsPage";
import { AppLayout } from "../shared/ui/layout";

export const router = createBrowserRouter([
  {
    path: "/operations-window",
    element: <OperationsWindowPage />,
  },
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <OverviewPage /> },
      { path: "triage", element: <TriagePage /> },
      { path: "devices", element: <DevicesPage /> },
      { path: "work-reports", element: <WorkReportsPage /> },
      { path: "tasks", element: <TasksPage /> },
      { path: "costs", element: <CostsPage /> },
      { path: "data-quality", element: <DataQualityPage /> },
      { path: "admin", element: <AdminDebugPage /> },
    ],
  },
]);
