"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Loader2, AlertCircle } from "lucide-react";
import api from "@/lib/api"; // API helper import

export default function PatientSignup() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  
  // Form States
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    age: "",
    gender: "Male",
    password: ""
  });

  const handleChange = (e: any) => {
    setFormData({ ...formData, [e.target.name]: e.target.value }); //NZ
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      // API Call to Register
      await api.post("/auth/register", {
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        role: "patient",
        age: parseInt(formData.age),
        gender: formData.gender
      });

      // Success -> Login page par bhejo
      router.push("/auth/patient/login");
      
    } catch (err: any) {
      console.error(err);
      if (err.response) {
        setError(err.response.data.detail || "Registration failed.");
      } else {
        setError("Server not reachable.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="text-center text-3xl font-bold text-slate-900">Create Patient Account</h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10 border-t-4 border-patient">
          
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded flex items-center gap-2">
              <AlertCircle className="h-4 w-4" /> {error}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleRegister}>
            <Input 
              label="Full Name" 
              name="full_name" 
              placeholder="John Doe" 
              onChange={handleChange} 
              required 
            />
            <Input 
              label="Email" 
              type="email" 
              name="email" 
              onChange={handleChange} 
              required 
            />
            
            <div className="grid grid-cols-2 gap-4">
               <Input 
                 label="Age" 
                 type="number" 
                 name="age" 
                 placeholder="25" 
                 onChange={handleChange} 
                 required 
               />
               <div className="space-y-2">
                 <label className="text-sm font-medium text-slate-700">Gender</label>
                 <select 
                   name="gender" 
                   onChange={handleChange}
                   className="flex h-10 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm focus:ring-2 focus:ring-patient/50 focus:outline-none"
                 >
                   <option value="Male">Male</option>
                   <option value="Female">Female</option>
                   <option value="Other">Other</option>
                 </select>
               </div>
            </div>
            
            <Input 
              label="Password" 
              type="password" 
              name="password" 
              onChange={handleChange} 
              required 
            />
            
            <Button variant="patient" className="w-full mt-4" size="lg" disabled={loading}>
              {loading ? <Loader2 className="animate-spin h-5 w-5"/> : "Register"}
            </Button>
          </form>
          
          <div className="mt-4 text-center text-sm">
            Already have an account? <Link href="/auth/patient/login" className="text-patient font-bold">Login</Link>
          </div>
        </div>
      </div>
    </div>
  );
}