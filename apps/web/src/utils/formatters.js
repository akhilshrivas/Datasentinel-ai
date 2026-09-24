export const formatDateTime = (dateString) => {
    if (!dateString) return 'Unavailable';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'Unavailable';
    return date.toLocaleString('en-US', {
        hour12: true,
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
};

export const formatTime = (dateString) => {
    if (!dateString) return 'Unavailable';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'Unavailable';
    return date.toLocaleTimeString('en-US', {
        hour12: true,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
};

export const formatDate = (dateString) => {
    if (!dateString) return 'Unavailable';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'Unavailable';
    return date.toLocaleDateString('en-US');
};
