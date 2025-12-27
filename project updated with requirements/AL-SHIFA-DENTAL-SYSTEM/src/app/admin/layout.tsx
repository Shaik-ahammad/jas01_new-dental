"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Stethoscope, Building2, FileText, Settings, LogOut } from "lucide-react";
import AppLayout from "@/layouts/AppLayout"; // Assuming this wraps generic providers

const NAV_ITEMS = [
  { label: "Dashboard", href: "/admin/dashboard", icon: LayoutDashboard },
  { label: "Doctor Queue", href: "/admin/doctors", icon: Stethoscope },
  { label: "Hospital Queue", href: "/admin/organizations", icon: Building2 },
  { label: "Audit Logs", href: "/admin/audit", icon: FileText },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col fixed h-full inset-y-0 z-50">
        <div className="p-6">
          <h2 className="text-xl font-bold text-white tracking-tight">Admin Console</h2>
          <p className="text-xs text-slate-500 mt-1">Al-Shifa Verification</p>
        </div>
        
        <nav className="flex-1 px-4 space-y-2 mt-4">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link 
                key={item.href} 
                href={item.href}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                  isActive 
                    ? "bg-blue-600 text-white shadow-lg shadow-blue-900/20" 
                    : "hover:bg-slate-800 hover:text-white"
                }`}
              >
                <item.icon className="h-5 w-5" />
                {item.label}
              </Link>
            )
          })}
        </nav>

        <div className="p-4 border-t border-slate-800">
          <button className="flex items-center gap-3 px-4 py-2 text-sm text-red-400 hover:text-red-300 transition-colors w-full">
            <LogOut className="h-4 w-4" /> Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 ml-64 p-8">
        <div className="max-w-6xl mx-auto">
           {children}
        </div>
      </main>
    </div>
  );
}