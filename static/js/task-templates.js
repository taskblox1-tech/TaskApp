/**
 * Pre-loaded Task Templates
 * Organized by category with default settings
 */

const TASK_TEMPLATES = {
    "Morning Tasks (Anyday)": [
        { title: "Eat Breakfast", icon: "🍳", points: 50, period: "morning", day_type: "anyday", requires_approval: false },
        { title: "Brush Teeth", icon: "🪥", points: 40, period: "morning", day_type: "anyday", requires_approval: false },
        { title: "Get Dressed", icon: "👕", points: 25, period: "morning", day_type: "anyday", requires_approval: false },
        { title: "Take Medicine", icon: "💊", points: 60, period: "morning", day_type: "anyday", requires_approval: false }
    ],

    "Morning Tasks (Weekday)": [
        { title: "Backpack Organized", icon: "🎒", points: 30, period: "morning", day_type: "weekday", requires_approval: false },
        { title: "Socks and Shoes", icon: "🧦", points: 20, period: "morning", day_type: "weekday", requires_approval: false },
        { title: "Fill Water Bottle for School", icon: "💧", points: 30, period: "morning", day_type: "weekday", requires_approval: false },
        { title: "Perfect Morning Routine", icon: "⭐", points: 85, period: "morning", day_type: "weekday", requires_approval: true, description: "All morning tasks done without reminders" }
    ],

    "Evening Tasks (Anyday)": [
        { title: "Doors Closed and Locked", icon: "🔒", points: 45, period: "evening", day_type: "anyday", requires_approval: false },
        { title: "Key Put Away", icon: "🔑", points: 25, period: "evening", day_type: "anyday", requires_approval: false },
        { title: "Shoes Put Away", icon: "👟", points: 30, period: "evening", day_type: "anyday", requires_approval: false },
        { title: "Room Clean", icon: "🧹", points: 60, period: "evening", day_type: "anyday", requires_approval: false },
        { title: "Reading 15 Minutes", icon: "📚", points: 70, period: "evening", day_type: "anyday", requires_approval: false },
        { title: "Laundry in Basement", icon: "👔", points: 40, period: "evening", day_type: "anyday", requires_approval: false },
        { title: "Gate Closed", icon: "🚪", points: 35, period: "evening", day_type: "anyday", requires_approval: false },
        { title: "Bedtime Routine On Time", icon: "🌙", points: 55, period: "evening", day_type: "anyday", requires_approval: false, description: "In bed at designated bedtime" }
    ],

    "Evening Tasks (Weekday)": [
        { title: "Homework Completed", icon: "📚", points: 80, period: "evening", day_type: "weekday", requires_approval: false },
        { title: "Study Session (30 min)", icon: "📖", points: 50, period: "evening", day_type: "weekday", requires_approval: false, description: "Focused studying without distractions" }
    ],

    "Evening Tasks (Weekend)": [
        { title: "Family Time Activity", icon: "👨‍👩‍👧", points: 80, period: "evening", day_type: "weekend", requires_approval: true },
        { title: "Reading 30 Minutes", icon: "📖", points: 100, period: "evening", day_type: "weekend", requires_approval: false },
        { title: "Prepare for Next Week", icon: "📅", points: 50, period: "evening", day_type: "weekend", requires_approval: false }
    ],

    "Academic Excellence": [
        { title: "Perfect Test/Quiz Score", icon: "💯", points: 150, period: "anytime", day_type: "anyday", requires_approval: true, description: "100% or A+ on any test or quiz" },
        { title: "Good Email from Teacher", icon: "✉️", points: 100, period: "anytime", day_type: "anyday", requires_approval: true, description: "Positive feedback from teacher" },
        { title: "Improved Grade", icon: "📈", points: 125, period: "anytime", day_type: "anyday", requires_approval: true, description: "Grade goes up in any subject" },
        { title: "Extra Credit Assignment", icon: "⭐", points: 80, period: "anytime", day_type: "anyday", requires_approval: true, description: "Completing optional work" },
        { title: "No Missing Assignments", icon: "✅", points: 90, period: "anytime", day_type: "anyday", requires_approval: true, description: "All homework turned in on time (weekly check)" }
    ],

    "Health & Fitness": [
        { title: "Exercise 20 Minutes", icon: "🏃", points: 60, period: "anytime", day_type: "anyday", requires_approval: false, description: "Running, biking, sports, or active play" },
        { title: "Drink 4 Glasses of Water", icon: "💧", points: 40, period: "anytime", day_type: "anyday", requires_approval: false, description: "Staying hydrated throughout day" },
        { title: "Healthy Snack Choice", icon: "🍎", points: 30, period: "anytime", day_type: "anyday", requires_approval: false, description: "Choosing fruit/vegetables over junk food" },
        { title: "Outside Play 30 Minutes", icon: "🌳", points: 50, period: "anytime", day_type: "anyday", requires_approval: false, description: "Fresh air and outdoor activity" }
    ],

    "Character & Behavior": [
        { title: "Act of Kindness", icon: "💖", points: 75, period: "anytime", day_type: "anyday", requires_approval: true, description: "Helping sibling, friend, or stranger without being asked" },
        { title: "Good Attitude All Day", icon: "😊", points: 60, period: "evening", day_type: "anyday", requires_approval: true, description: "No complaining, positive interactions" },
        { title: "Respectful Communication", icon: "🗣️", points: 50, period: "anytime", day_type: "anyday", requires_approval: true, description: "Using please/thank you, speaking politely" },
        { title: "Sharing with Sibling", icon: "🤝", points: 40, period: "anytime", day_type: "anyday", requires_approval: true, description: "Sharing toys, games, or activities willingly" },
        { title: "Following Directions First Time", icon: "👂", points: 45, period: "anytime", day_type: "anyday", requires_approval: true, description: "Listening and responding immediately" }
    ],

    "Extra Household Tasks": [
        { title: "Help Make Dinner", icon: "🍳", points: 65, period: "evening", day_type: "anyday", requires_approval: false, description: "Assisting with meal preparation" },
        { title: "Set/Clear Table", icon: "🍽️", points: 35, period: "evening", day_type: "anyday", requires_approval: false, description: "Mealtime responsibilities" },
        { title: "Take Out Trash", icon: "🗑️", points: 45, period: "anytime", day_type: "anyday", requires_approval: false, description: "Without being asked" },
        { title: "Vacuum/Sweep Room", icon: "🧹", points: 55, period: "anytime", day_type: "weekend", requires_approval: false, description: "Deep cleaning task" },
        { title: "Organize Closet/Drawers", icon: "👔", points: 70, period: "anytime", day_type: "weekend", requires_approval: false, description: "Folding and organizing clothes" },
        { title: "Help with Laundry", icon: "🧺", points: 50, period: "anytime", day_type: "weekend", requires_approval: false, description: "Sorting, folding, or putting away" },
        { title: "Clean Bathroom", icon: "🚽", points: 80, period: "anytime", day_type: "weekend", requires_approval: false, description: "Sink, mirror, counter" },
        { title: "Help with Chores", icon: "🏠", points: 70, period: "anytime", day_type: "anyday", requires_approval: false, description: "General household help" }
    ],

    "Creative & Personal Development": [
        { title: "Practice Instrument", icon: "🎹", points: 60, period: "anytime", day_type: "anyday", requires_approval: false, description: "Music practice session" },
        { title: "Art/Drawing Project", icon: "🎨", points: 50, period: "anytime", day_type: "anyday", requires_approval: false, description: "Creative expression" },
        { title: "Journal Entry", icon: "📔", points: 40, period: "evening", day_type: "anyday", requires_approval: false, description: "Writing thoughts or daily reflection" },
        { title: "Learn Something New", icon: "🧠", points: 75, period: "anytime", day_type: "anyday", requires_approval: true, description: "Teaching family about new topic learned" }
    ],

    "Bonus Challenges": [
        { title: "Zero Screen Time Day", icon: "📵", points: 200, period: "anytime", day_type: "anyday", requires_approval: true, description: "Full day without TV, tablet, or games" },
        { title: "Read Entire Book", icon: "📚", points: 150, period: "anytime", day_type: "anyday", requires_approval: true, description: "Complete age-appropriate book" },
        { title: "Complete Weekly Goal", icon: "🎯", points: 100, period: "anytime", day_type: "weekend", requires_approval: true, description: "Achieve personal goal set at week start" }
    ]
};

// Helper function to get all categories
function getTaskCategories() {
    return Object.keys(TASK_TEMPLATES);
}

// Helper function to get tasks by category
function getTasksByCategory(category) {
    return TASK_TEMPLATES[category] || [];
}

// Helper function to get all tasks flattened
function getAllTaskTemplates() {
    const allTasks = [];
    for (const category in TASK_TEMPLATES) {
        TASK_TEMPLATES[category].forEach(task => {
            allTasks.push({
                ...task,
                category: category
            });
        });
    }
    return allTasks;
}
