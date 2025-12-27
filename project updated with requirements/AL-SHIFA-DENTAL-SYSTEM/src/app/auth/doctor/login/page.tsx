"use client";
import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Stethoscope, Loader2, AlertCircle } from "lucide-react";
import { AuthAPI } from "@/lib/api"; // FIX: Import AuthAPI

export default function DoctorLogin() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // FIX: Use AuthAPI.login (Calls /auth/login with FormData)
      const response = await AuthAPI.login(email, password);

      // Role Check
      if (response.data.role !== "doctor") {
        setError("Access Denied: This portal is for Doctors only.");
        return;
      }

      localStorage.setItem("token", response.data.access_token);
      localStorage.setItem("role", response.data.role);
      
      router.push("/doctor/dashboard");

    } catch (err: any) {
      console.error(err);
      setError("Invalid credentials or server error.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="h-12 w-12 rounded-full bg-indigo-100 flex items-center justify-center">
            <Stethoscope className="h-6 w-6 text-indigo-600" />
          </div>
        </div>
        <h2 className="mt-6 text-center text-3xl font-bold tracking-tight text-slate-900">
          Doctor Portal
        </h2>
        <p className="mt-2 text-center text-sm text-slate-600">
          Secure access for medical staff
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10 border-t-4 border-indigo-600">
          
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded flex items-center gap-2">
              <AlertCircle className="h-4 w-4" /> {error}
            </div>
          )}

          <form className="space-y-6" onSubmit={handleLogin}>
            <Input 
              label="Professional Email" 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Input 
              label="Password" 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            <div className="flex items-center justify-between">
              <div className="text-sm">
                <Link 
                  href="/auth/doctor/forgot-password" 
                  className="font-medium text-indigo-600 hover:text-indigo-500 hover:underline"
                >
                  Forgot password?
                </Link>
              </div>
            </div>

            <Button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white" size="lg" disabled={loading}>
              {loading ? <Loader2 className="animate-spin h-5 w-5"/> : "Sign In"}
            </Button>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-300" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="bg-white px-2 text-slate-500">Not registered?</span>
              </div>
            </div>
            <div className="mt-6">
              <Link href="/auth/doctor/signup">
                <Button variant="outline" className="w-full border-slate-300 text-slate-700 hover:bg-slate-50">
                  Apply for Verification
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}