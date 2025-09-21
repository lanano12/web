import React, { Suspense, useState, useTransition } from "react";
import { motion } from "framer-motion";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

function generateData() {
  return Array.from({ length: 20 }, (_, i) => ({
    x: i,
    y: Math.sin(i / 3) + Math.random() * 0.5,
  }));
}

const Chart = () => {
  const data = generateData();
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <XAxis dataKey="x" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="y" stroke="#82ca9d" />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default function App() {
  const [theme, setTheme] = useState("dark");
  const [isPending, startTransition] = useTransition();
  const [showChart, setShowChart] = useState(true);

  return (
    <div className={theme === "dark" ? "bg-gray-900 text-white min-h-screen" : "bg-white text-black min-h-screen"}>
      <header className="p-6 flex justify-between items-center shadow-md">
        <h1 className="text-3xl font-bold">⚡ Spectra Demo</h1>
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="px-4 py-2 rounded bg-indigo-600 text-white hover:bg-indigo-700"
        >
          Toggle {theme === "dark" ? "Light" : "Dark"} Mode
        </button>
      </header>

      <main className="p-6 space-y-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center"
        >
          <h2 className="text-2xl font-semibold">React Features Showcase</h2>
          <p className="text-gray-400">Concurrent Rendering, Suspense, Animations, and Charts</p>
        </motion.div>

        <div className="text-center">
          <button
            className="px-6 py-3 bg-green-600 rounded-lg hover:bg-green-700"
            onClick={() => startTransition(() => setShowChart((prev) => !prev))}
          >
            {isPending ? "Loading..." : showChart ? "Hide Chart" : "Show Chart"}
          </button>
        </div>

        <Suspense fallback={<p className="text-center">Loading chart...</p>}>
          {showChart && <Chart />}
        </Suspense>
      </main>
    </div>
  );
}
