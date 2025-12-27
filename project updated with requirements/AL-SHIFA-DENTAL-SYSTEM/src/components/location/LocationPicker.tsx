"use client";

import { useState } from "react";
import { MapPin, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

type LocationData = { address: string; pincode: string; lat?: number; lng?: number };

type Props = {
  onChange: (loc: LocationData) => void;
  initialData?: Partial<LocationData>;
};

export default function LocationPicker({ onChange, initialData }: Props) {
  const [address, setAddress] = useState(initialData?.address || "");
  const [pincode, setPincode] = useState(initialData?.pincode || "");

  const emit = () => onChange({ address, pincode });

  const handleDetectLocation = () => {
    // Simulation of Geolocation API
    setAddress("123 Detected St, Tech Park");
    setPincode("500081");
    onChange({ address: "123 Detected St, Tech Park", pincode: "500081" });
  };

  return (
    <div className="space-y-3 bg-slate-50 p-4 rounded-lg border border-slate-200">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-slate-700 flex items-center gap-2">
          <MapPin className="h-4 w-4 text-blue-500" /> Clinic Location
        </label>
        <Button 
          type="button" 
          variant="ghost" 
          size="sm" 
          onClick={handleDetectLocation}
          className="text-xs text-blue-600 h-8"
        >
          Detect Current Location
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="md:col-span-2">
            <Input
              placeholder="Street Address, City"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
              onBlur={emit}
              className="bg-white"
            />
        </div>
        <div>
            <Input
              placeholder="Pincode"
              value={pincode}
              onChange={(e) => setPincode(e.target.value)}
              onBlur={emit}
              className="bg-white"
              maxLength={6}
            />
        </div>
      </div>
      <p className="text-[10px] text-slate-500 flex items-center gap-1">
        <Search className="h-3 w-3" /> Address helps patients find you via navigation apps.
      </p>
    </div>
  );
}