import { Star } from "lucide-react";

export function RatingStars({ rating, size = "sm" }: { rating: number; size?: "sm" | "md" | "lg" }) {
  const sizes = {
    sm: "h-3.5 w-3.5",
    md: "h-4 w-4",
    lg: "h-5 w-5",
  };

  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <Star
          key={star}
          className={`${sizes[size]} ${
            rating >= star
              ? "fill-amber-400 text-amber-400"
              : rating >= star - 0.5
              ? "fill-amber-200 text-amber-400"
              : "text-slate-300"
          }`}
        />
      ))}
      <span className="ml-1 font-bold text-amber-700 text-sm">{rating.toFixed(1)}</span>
    </div>
  );
}
