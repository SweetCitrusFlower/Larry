import React from 'react';

const Sidebar = () => {
  const mockFiles = [
    { name: 'src', type: 'folder', children: [
      { name: 'main.py', type: 'file' },
      { name: 'utils.py', type: 'file' },
    ]},
    { name: 'tests', type: 'folder', children: [
      { name: 'test_api.py', type: 'file' },
    ]},
    { name: 'requirements.txt', type: 'file' },
    { name: 'README.md', type: 'file' },
  ];

  const renderTree = (items) => (
    <ul className="file-list">
      {items.map((item, index) => (
        <li key={index} className="file-item">
          <div className={`file-label ${item.type}`}>
            {item.type === 'folder' ? (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="icon-folder">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
              </svg>
            ) : (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="icon-file">
                <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                <polyline points="13 2 13 9 20 9"></polyline>
              </svg>
            )}
            <span>{item.name}</span>
          </div>
          {item.children && renderTree(item.children)}
        </li>
      ))}
    </ul>
  );

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h3>FILES</h3>
        <div className="sidebar-actions">
          <button title="New File">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          </button>
          <button title="New Folder">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path><line x1="12" y1="11" x2="12" y2="17"></line><line x1="9" y1="14" x2="15" y2="14"></line></svg>
          </button>
        </div>
      </div>
      <div className="file-explorer">
        {renderTree(mockFiles)}
      </div>

    </aside>
  );
};

export default Sidebar;
