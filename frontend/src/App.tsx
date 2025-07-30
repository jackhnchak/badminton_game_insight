import React from 'react';
import UploadForm from './components/UploadForm';

const App: React.FC = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <UploadForm />
    </div>
  );
};

export default App;