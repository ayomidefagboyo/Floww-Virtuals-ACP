# Floww Virtuals Dashboard

A premium AI trading agents dashboard built with Next.js, featuring a Swiss spa-inspired minimalist design.

## Features

- **3 AI Trading Agents**:
  - **Ryu Agent**: Professional token analysis with balanced risk
  - **Yuki Agent**: High-frequency trading with aggressive strategies
  - **LLM Analysis**: Claude-powered market insights and sentiment

- **Premium Design System**:
  - Swiss spa minimalist aesthetic
  - Cohesive color palette with dark theme
  - Responsive mobile/desktop layouts
  - Smooth animations and micro-interactions

- **Real-time Monitoring**:
  - Live agent status indicators
  - Performance metrics and P&L tracking
  - Portfolio overview with key statistics
  - Professional data visualization

## Design Philosophy

- **Steve Jobs Standard**: Obsessive attention to detail and user experience
- **Professional Web3**: Sophisticated but engaging interface
- **Premium Feel**: Swiss spa-level quality that justifies premium pricing
- **Responsive**: Perfect on both desktop and mobile devices

## Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS with custom design system
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Fonts**: Inter (UI), JetBrains Mono (data)

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Run development server**:
   ```bash
   npm run dev
   ```

3. **Open browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript checks

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001
```

## Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── AgentCard.tsx    # Agent display card
│   │   └── Dashboard.tsx    # Main dashboard
│   ├── pages/           # Next.js pages
│   ├── services/        # API services
│   ├── styles/          # Global styles
│   ├── types/           # TypeScript types
│   └── utils/           # Utility functions
├── public/              # Static assets
└── config files
```

## Design System

### Colors
- **Primary**: Deep charcoal backgrounds
- **Secondary**: Pure white cards and text
- **Accent**: Electric blue highlights
- **Success**: Emerald green for positive metrics
- **Warning**: Amber for caution states
- **Error**: Ruby red for negative metrics

### Typography
- **UI Font**: Inter (clean, professional)
- **Data Font**: JetBrains Mono (metrics, numbers)
- **6-level hierarchy** with proper line heights

### Spacing
- **Base unit**: 4px
- **System**: 8px, 16px, 24px, 32px, 48px
- **Perfect spacing** between all components

### Components
- **Cards**: Elevated with subtle shadows and rounded corners
- **Buttons**: Multiple variants (primary, secondary, ghost)
- **Status**: Color-coded indicators with animations
- **Metrics**: Large numbers with muted labels

## API Integration

The dashboard connects to the backend API at `localhost:8001`:

- `/api/agents` - Get all agents
- `/api/agents/{id}` - Get specific agent
- `/api/agents/{id}/start|stop` - Control agents
- `/api/market/overview` - Market data
- `/api/signals` - Recent trade signals

Mock data is used when API is unavailable for seamless development.

## Responsive Design

- **Mobile**: 320px - 768px (single column)
- **Tablet**: 768px - 1024px (adaptive grid)
- **Desktop**: 1024px+ (full 3-column layout)

Perfect touch targets and optimized layouts for all screen sizes.

## Performance

- Lazy loading for agent data
- Debounced API calls
- Efficient React re-rendering
- Optimized bundle splitting
- Progressive image loading

## Accessibility

- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader optimizations
- High contrast mode support
- Focus management

---

Built with ❤️ for premium AI trading experiences.