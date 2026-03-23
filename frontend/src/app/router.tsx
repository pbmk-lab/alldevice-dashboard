import { createBrowserRouter } from "react-router-dom";

import { AdminDebugPage } from "../features/admin-debug/AdminDebugPage";
import { DataQualityPage } from "../features/data-quality/DataQualityPage";
import { DevicesPage } from "../features/devices/DevicesPage";
import { OverviewPage } from "../features/overview/OverviewPage";
import { TriagePage } from "../features/triage/TriagePage";
import { WorkReportsPage } from "../features/work-reports/WorkReportsPage";
import { AppLayout } from "../shared/ui/layout";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <OverviewPage /> },
      { path: "triage", element: <TriagePage /> },
      { path: "devices", element: <DevicesPage /> },
      { path: "work-reports", element: <WorkReportsPage /> },
      { path: "data-quality", element: <DataQualityPage /> },
      { path: "admin", element: <AdminDebugPage /> },
    ],
  },
]);
