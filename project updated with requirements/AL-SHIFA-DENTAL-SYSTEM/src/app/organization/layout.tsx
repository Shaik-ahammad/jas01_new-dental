"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Users, UserCog, Building, Menu, X } from "lucide-react";
import { Button } from "@/components/ui/button";

const ORG_NAV = [
  { label: "Dashboard", href: "/organization/dashboard", icon: LayoutDashboard },
  { label: "My Profile", href: "/organization/profile", icon: Building },
  { label: "Doctors & Staff", href: "/organization/doctors", icon: Users },
  { label: "Appointments", href: "/organization/appointments", icon: UserCog }, // Anticipating future need
];

export default function OrganizationLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [isSidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Mobile Toggle */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <Button size="icon" variant="outline" onClick={() => setSidebarOpen(!isSidebarOpen)}>
            {isSidebarOpen ? <X className="h-4 w-4"/> : <Menu className="h-4 w-4"/>}
        </Button>
      </div>

      {/* Sidebar */}
      <aside className={`
        fixed lg:static inset-y-0 left-0 z-40 w-64 bg-white border-r border-gray-200 transform transition-transform duration-200 ease-in-out
        ${isSidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"}
      `}>
        <div className="h-16 flex items-center px-6 border-b border-gray-100">
          <span className="text-lg font-bold text-blue-600">Al-Shifa Partner</span>
        </div>

        <nav className="p-4 space-y-1">
          {ORG_NAV.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link 
                key={item.href} 
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive 
                    ? "bg-blue-50 text-blue-700" 
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-900"
                }`}
              >
                <item.icon className={`h-4 w-4 ${isActive ? "text-blue-600" : "text-gray-400"}`} />
                {item.label}
              </Link>
            )
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 lg:p-10 overflow-y-auto">
        <div className="max-w-5xl mx-auto space-y-8">
            {children}
        </div>
      </main>
    </div>
  );
}