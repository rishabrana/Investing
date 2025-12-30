import { Info, ExternalLink } from 'lucide-react';
import { useState, useRef, useEffect } from 'react';

interface InfoIconProps {
  description: string;
  learnMoreUrl?: string;
  size?: 'sm' | 'md';
}

export function InfoIcon({ description, learnMoreUrl, size = 'sm' }: InfoIconProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [tooltipPosition, setTooltipPosition] = useState({ top: 0, left: 0 });
  const iconRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);
  const hideTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isVisible && iconRef.current) {
      const rect = iconRef.current.getBoundingClientRect();
      const tooltipWidth = 280; // Approximate tooltip width
      const viewportWidth = window.innerWidth;

      // Calculate position to keep tooltip in viewport
      let left = rect.left;
      if (left + tooltipWidth > viewportWidth - 20) {
        left = viewportWidth - tooltipWidth - 20;
      }

      setTooltipPosition({
        top: rect.bottom + window.scrollY + 8,
        left: left + window.scrollX,
      });
    }
  }, [isVisible]);

  const handleMouseEnter = () => {
    // Clear any pending hide timeout
    if (hideTimeoutRef.current) {
      clearTimeout(hideTimeoutRef.current);
      hideTimeoutRef.current = null;
    }
    setIsVisible(true);
  };

  const handleMouseLeave = () => {
    // Add a delay before hiding to allow mouse to move to tooltip
    hideTimeoutRef.current = setTimeout(() => {
      setIsVisible(false);
    }, 200); // 200ms delay
  };

  const handleTooltipMouseEnter = () => {
    // Clear hide timeout when mouse enters tooltip
    if (hideTimeoutRef.current) {
      clearTimeout(hideTimeoutRef.current);
      hideTimeoutRef.current = null;
    }
  };

  const handleTooltipMouseLeave = () => {
    // Hide immediately when leaving tooltip
    setIsVisible(false);
  };

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (hideTimeoutRef.current) {
        clearTimeout(hideTimeoutRef.current);
      }
    };
  }, []);

  const iconSize = size === 'sm' ? 'w-3.5 h-3.5' : 'w-4 h-4';

  return (
    <div
      ref={iconRef}
      className="relative inline-block"
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <Info className={`${iconSize} text-gray-400 hover:text-blue-500 cursor-help transition-colors`} />

      {isVisible && (
        <div
          ref={tooltipRef}
          className="fixed z-50 bg-white rounded-lg shadow-lg border border-gray-200 p-3 max-w-[280px]"
          style={{
            top: `${tooltipPosition.top}px`,
            left: `${tooltipPosition.left}px`,
          }}
          onMouseEnter={handleTooltipMouseEnter}
          onMouseLeave={handleTooltipMouseLeave}
        >
          <p className="text-xs text-gray-700 leading-relaxed mb-2">
            {description}
          </p>

          {learnMoreUrl && (
            <a
              href={learnMoreUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 font-medium transition-colors"
              onClick={(e) => e.stopPropagation()}
            >
              <span>Learn more</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>
      )}
    </div>
  );
}
