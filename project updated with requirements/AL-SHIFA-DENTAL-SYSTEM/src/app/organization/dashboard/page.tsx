import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Users, Calendar, ShieldCheck, ArrowUpRight } from "lucide-react";

export default function OrgDashboard() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Hospital Overview</h1>
        <span className="text-sm text-gray-500">Last updated: Just now</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Active Doctors KPI */}
        <Card className="shadow-sm border-l-4 border-l-blue-600">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Active Doctors</CardTitle>
            <Users className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">18</div>
            <p className="text-xs text-gray-500 mt-1 flex items-center">
              <span className="text-green-600 flex items-center mr-1">
                <ArrowUpRight className="h-3 w-3" /> +2
              </span> 
              this month
            </p>
          </CardContent>
        </Card>

        {/* Appointments KPI */}
        <Card className="shadow-sm border-l-4 border-l-purple-600">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">Appointments Today</CardTitle>
            <Calendar className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">42</div>
            <p className="text-xs text-gray-500 mt-1">6 pending confirmation</p>
          </CardContent>
        </Card>

        {/* Status KPI */}
        <Card className="shadow-sm border-l-4 border-l-green-600">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-gray-500">KYC Status</CardTitle>
            <ShieldCheck className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold text-green-700">Verified</div>
            <p className="text-xs text-gray-500 mt-1">License valid till Dec 2025</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}