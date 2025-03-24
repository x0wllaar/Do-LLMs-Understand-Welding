vim.api.nvim_create_autocmd({"BufWritePost"}, {
  pattern = {"*.py"},
  callback = function(args) 
      local file_name = args.file
      vim.fn.system {'black', '--line-length', '75', file_name}
      vim.fn.system {'isort', file_name} 
      vim.cmd("checktime")
  end,
})
