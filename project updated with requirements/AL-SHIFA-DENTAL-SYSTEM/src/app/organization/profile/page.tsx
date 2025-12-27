import LocationSummary from "@/components/location/LocationSummary";
import { Badge } from "@/components/ui/badge"; // Assuming standard UI badge
import { Button } from "@/components/ui/button";
import { Building2, Edit } from "lucide-react";

export default function OrgProfile() {
  // Mock Data
  const org = {
    name: "Al-Shifa Dental Center",
    type: "Multi-Specialty Clinic",
    reg_no: "REG-HYD-9988",
    address: "Road No. 12, Banjara Hills",
    pincode: "500034",
    kycStatus: "Verified"
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Hospital Profile</h1>
        <Button variant="outline" size="sm">
          <Edit className="h-4 w-4 mr-2" /> Edit Details
        </Button>
      </div>

      {/* Main Info Card */}
      <div className="bg-white p-6 rounded-xl border shadow-sm space-y-6">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600">
              <Building2 className="h-8 w-8" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-900">{org.name}</h2>
              <p className="text-sm text-gray-500">{org.type}</p>
              <div className="mt-2 flex items-center gap-2">
                 <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200">
                    {org.kycStatus}
                 </Badge>
                 <span className="text-xs text-gray-400">Reg No: {org.reg_no}</span>
              </div>
            </div>
          </div>
        </div>

        <hr />

        {/* Location Section */}
        <div>
          <h3 className="text-sm font-medium text-gray-900 mb-3">Location & Access</h3>
          <LocationSummary address={org.address} pincode={org.pincode} />
        </div>
      </div>
    </div>
  );
}