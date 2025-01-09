"use client";
import DisplayTables from "@/components/display-tables";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { DUMMY_DATA } from "@/constants/dummyData";
import { ArrowLeft, LoaderCircle } from "lucide-react";
import React, { useState } from "react";

const HomePage = () => {
  const [tables, setTables] = useState();
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState();

  const handlePdfUpload = async () => {
    setLoading(true);
    try {
      if (!file) throw new Error("Please select a file to upload");
      const formData = new FormData();
      formData.append("file", file);

      const response = await (
        await fetch(process.env.NEXT_PUBLIC_API_URL + "/api/extract", {
          method: "POST",
          body: formData,
        })
      ).json();

      if (!response.success) throw new Error(response.message);

      setTables(response.tables);
    } catch (error) {
      alert(error.message);
    }
    setLoading(false);
  };
  return (
    <div className="container p-8">
      {!tables ? (
        <div className="space-y-8">
          <div className="flex justify-center items-center gap-4">
            <Input
              type="file"
              accept="application/pdf"
              onChange={(e) => setFile(e.target.files[0])}
              disabled={loading}
            />
            <Button disabled={loading} onClick={handlePdfUpload}>
              {loading && <LoaderCircle className="animate-spin" />}
              Upload PDF & Extract
            </Button>
          </div>
          <Button
            onClick={() => setTables(DUMMY_DATA.tables)}
            disabled={loading}
          >
            View Sample Extracted Data
          </Button>
        </div>
      ) : (
        <>
          <Button onClick={() => setTables()}>
            <ArrowLeft />
            Back
          </Button>
          <DisplayTables tables={tables} />
        </>
      )}
    </div>
  );
};

export default HomePage;
