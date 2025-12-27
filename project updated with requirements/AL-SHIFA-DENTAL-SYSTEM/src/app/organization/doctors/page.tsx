import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { MoreHorizontal, Plus, Stethoscope } from "lucide-react";

const DOCTORS = [
  { id: "DOC_1", name: "Dr. John Doe", specialization: "Orthodontist", status: "Active" },
  { id: "DOC_2", name: "Dr. Sarah Lee", specialization: "Pediatric Dentist", status: "Active" },
  { id: "DOC_3", name: "Dr. Ahmed Khan", specialization: "Oral Surgeon", status: "On Leave" },
];

export default function OrgDoctors() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Doctors & Staff</h1>
          <p className="text-sm text-gray-500">Manage practitioners linked to this facility.</p>
        </div>
        <Button className="bg-blue-600 hover:bg-blue-700">
          <Plus className="h-4 w-4 mr-2" /> Add Doctor
        </Button>
      </div>

      <div className="border rounded-xl bg-white shadow-sm overflow-hidden">
        <table className="w-full text-sm text-left">
          <thead className="bg-gray-50 text-gray-500 font-medium border-b">
            <tr>
              <th className="p-4">Name</th>
              <th className="p-4">Specialization</th>
              <th className="p-4">Status</th>
              <th className="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {DOCTORS.map((d) => (
              <tr key={d.id} className="hover:bg-gray-50 transition-colors">
                <td className="p-4">
                  <div className="flex items-center gap-3">
                    <Avatar className="h-9 w-9">
                      <AvatarImage src={`https://api.dicebear.com/7.x/initials/svg?seed=${d.name}`} />
                      <AvatarFallback>DR</AvatarFallback>
                    </Avatar>
                    <span className="font-medium text-gray-900">{d.name}</span>
                  </div>
                </td>
                <td className="p-4 text-gray-600">
                  <div className="flex items-center gap-2">
                    <Stethoscope className="h-3 w-3 text-gray-400" />
                    {d.specialization}
                  </div>
                </td>
                <td className="p-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    d.status === "Active" ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
                  }`}>
                    {d.status}
                  </span>
                </td>
                <td className="p-4 text-right">
                  <Button variant="ghost" size="icon">
                    <MoreHorizontal className="h-4 w-4 text-gray-400" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}